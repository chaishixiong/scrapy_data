# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
from urllib import parse
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

class AmazonSortShop(RedisSpider):
    name = 'amazon_sortshop'
    allowed_domains = ['amazon.com']
    start_urls = ['http://www.amazon.com/']
    redis_key = "amazon_sortshop:start_url"
    error_key = "amazon_sortshop:error_url"
    custom_settings = {"DOWNLOAD_DELAY":1,"DOWNLOADER_MIDDLEWARES":{'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,
                                                                    'nriat_spider.middlewares.UserAgentChangeDownloaderMiddleware':20
}}
    headers = '''Host: www.amazon.com
User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36
accept-encoding: gzip, deflate, br
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Connection: keep-alive
accept-language: zh-CN,zh;q=0.9
upgrade-insecure-requests: 1'''
    def make_requests_from_url(self, seed):
        data = seed.split(",")
        url = data[0]
        url = parse.unquote(url)
        sort = data[1]
        return scrapy.Request(url=url, method="GET", headers=headers_todict(self.headers),meta={"sort":sort,"proxy":"127.0.0.1:8080"},dont_filter=True)

    def parse(self, response):
        youxiao = re.search("(refinementList|pagnLink)",response.text)
        sort = response.meta.get("sort")
        if youxiao:
            print("成功")
            shop_list = response.css("#refinementList").xpath("./div/ul/li")
            for i in shop_list:
                seller_url = i.xpath(".//a/@href").get("")
                seller_id = ""
                match = re.search('Cp_6%3A([^"]*?)(&|$)',seller_url)
                if match:
                    seller_id = match.group(1)
                seller_name = i.xpath(".//a/span[1]/text()").get()
                seller_goods = i.xpath(".//a/span[2]/text()").get()
                goods_num = re.sub("\D","",seller_goods)
                item = GmWorkItem()
                item["shop_url"] = seller_url
                item["shop_id"] = seller_id
                item["shop_name"] = seller_name
                item["goods_num"] = goods_num
                item["sort"] = sort
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