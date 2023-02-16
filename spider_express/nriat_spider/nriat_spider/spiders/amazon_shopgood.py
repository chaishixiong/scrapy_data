# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
from twisted.web.http_headers import Headers as TwistedHeaders

TwistedHeaders._caseMappings.update({
    b'Host': b'host',
    b'User-Agent': b'user-agent',
    b'accept-encoding': b'accept-encoding',
    b'accept': b'accept',
    b'Connection': b'connection',
    b'accept-language': b'accept-language',
    b'upgrade-insecure-requests': b'upgrade-insecure-requests'
})


class AmazonShopGoods(RedisSpider):
    name = 'amazon_shopgoods'
    allowed_domains = ['amazon.com']
    start_urls = ['http://www.amazon.com/']
    redis_key = "amazon_shopgoods:start_url"
    error_key = "amazon_shopgoods:error_url"
    custom_settings = {"DOWNLOAD_DELAY":1,"DOWNLOADER_MIDDLEWARES":{
    'nriat_spider.middlewares.IpChangeDownloaderMiddleware': 20,
    'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,
    'nriat_spider.middlewares.UserAgentChangeDownloaderMiddleware': 22,
}}
    headers = '''Host: www.amazon.com
User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36
accept-encoding: gzip, deflate, br
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Connection: keep-alive
accept-language: zh-CN,zh;q=0.9
upgrade-insecure-requests: 1'''
    def make_requests_from_url(self,seed):
        id = seed.strip()
        url = "https://www.amazon.com/s?me={}&language=en_US".format(id)
        return scrapy.Request(url=url, method="GET", headers=headers_todict(self.headers),dont_filter=True,meta={"id":id,"proxy":"127.0.0.1:8080","first":True})


    def parse(self, response):
        youxiao = re.search("(s-result-list|checking your|search-results|general terms)",response.text)
        id = response.meta.get("id")

        first = response.meta.get("first")
        if youxiao:
            item_s = GmWorkItem()
            item_s["id"] = id
            item_s["source_code"] = response.text
            yield item_s
            goods_num = ""
            match = re.search('"totalResultCount":(\d+)',response.text)
            if match:
                goods_num = match.group(1)

            if first and goods_num:
                page_num = int(int(goods_num)/16)+1 if int(goods_num)%16 else int(int(goods_num)/16)
                page_num = 10 if page_num>10 else page_num
                for i in range(2,page_num+1):
                    url = "https://www.amazon.com/s?me={}&language=en_US&page={}".format(id,i)
                    yield scrapy.Request(url=url, method="GET", headers=headers_todict(self.headers), dont_filter=True,
                                          meta={"id": id, "proxy": "127.0.0.1:8080"})

            goods_list = response.css(".s-main-slot.s-result-list.s-search-results.sg-row").xpath("./div")
            brand_list = response.css("#brandsRefinements").xpath("./ul/li")
            brands = []
            for i in brand_list:
                brand_name = i.xpath("./span/a/span/text()").get()
                if brand_name:
                    brands.append(brand_name)
            for goods in goods_list:
                goods_name = goods.css(".a-size-medium.a-color-base.a-text-normal").xpath("./text()").get()
                comment_score_s = goods.css(".a-icon-alt").xpath("./text()").get("")
                match1 = re.search("^([\d\.]+)",comment_score_s)
                comment_score = ""
                if match1:
                    comment_score = match1.group(1)
                comment_num = goods.css(".a-row.a-size-small").xpath("./span[2]/@aria-label").get("")
                comment_num = re.sub(r"\D","",comment_num)
                goods_url = goods.css(".a-size-medium.a-color-base.a-text-normal").xpath("./parent::a/@href").get()
                price_s = goods.css(".a-offscreen").xpath("./text()").get("")
                match2 = re.search("([\d\.]+)",price_s)
                price = ""
                if match2:
                    price = match2.group(1)
                goods_id = goods.xpath("./@data-asin").get()

                if goods_id:
                    item = GmWorkItem()
                    item["shop_id"] = id
                    item["goods_name"] = goods_name
                    item["comment_score"] = comment_score
                    item["comment_num"] = comment_num
                    item["goods_url"] = goods_url
                    item["price"] = price
                    item["goods_id"] = goods_id
                    item["goods_num"] = goods_num
                    item["brand"] = str(brands)
                    yield item
        else:
            try_result = self.try_again(response)
            yield try_result

    def try_again(self,rsp):
        max_num = 5
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num < max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request
        else:
            request = rsp.request
            request.meta["try_num"] = 0
            obj = request_to_dict(request, self)
            data = picklecompat.dumps(obj)
            try:
                self.server.lpush(self.error_key, data)
            except Exception as e:
                print(e)
