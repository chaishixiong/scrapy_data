# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
import redis,json
import time

class JdidSpider(RedisSpider):
    name = 'jd_id'
    allowed_domains = ['jd.id']
    start_urls = ['']
    redis_key = "jd_id:start_url"
    # server1 = redis.Redis(host='192.168.0.226', port=5208, decode_responses=True)
    error_key = "jd_id:error_url"
    area_num = [(1,60000),(10000000,10030000)]

    def start_requests(self):
        url = "http://www.baidu.com"
        yield scrapy.Request(url=url, method="GET",callback=self.seed_request)

    def seed_request(self,response):
        headers = self.get_headers(1)
        for i in self.area_num:
            for j in range(i[0],i[1]):
                vender_id = str(j)
                url = "https://www.jd.id/shop/{}/list.html".format(vender_id)
                yield scrapy.Request(url=url,method="GET",callback=self.shop_saomiao,headers=headers,meta={"vender_id":vender_id},dont_filter=True)

    def shop_saomiao(self,response):
        vender_id = response.meta.get("vender_id")
        match = re.search("shop-name",response.text)
        if match or response.status==302:
            item_s = GmWorkItem()
            item_s["key"] = vender_id
            item_s["pipeline_level"] = "shop"
            item_s["source_code"] = response.text
            yield item_s
            headers = self.get_headers(2)
            shop_name = response.css(".shop-name").xpath("./text()").get()#
            fan_num = response.css(".shop-follow").xpath("./span/text()").get()#
            category_list = []#
            categories = response.css(".nav-categories").xpath("./li")
            for i in categories:
                data_id = i.xpath("./@data-id").get("")
                cat_name = i.xpath("./span/text()").get("")
                cat_num = i.xpath("./text()").get("")
                category_list.append([data_id,cat_name,cat_num])
            page_num = response.css(".page-info").xpath("./text()").get(0)
            if page_num:
                match = re.search("(\d+)",page_num)
                if match:
                    page_num = int(match.group(1))
                    if page_num > 100:
                        page_num = 100

            if shop_name:
                item = GmWorkItem()
                item["vender_id"] = vender_id
                item["shop_name"] = shop_name
                item["fans"] = fan_num
                item["categorys"] = category_list
                item["page_num"] = page_num*20
                item["pipeline_level"] = "shop_info"
                yield item
                for i in range(1,page_num+1):
                    page_num = i
                    url = "https://color.jd.id/shop_decoration_ina/search/2.0?pageSize=20&mergeSku=true&venderId={}&pageNo={}&orderBy=2&catLevel=-1&filters=%7B%7D".format(vender_id,page_num)
                    data = '{{"pageSize":20,"mergeSku":true,"venderId":{},"pageNo":{},"orderBy":2,"catLevel":-1,"filters":"{{}}"}}'.format(vender_id,page_num)
                    headers["referer"] = "https://m.jd.id/shop/{}.html.html".format(vender_id)
                    headers["X-API-Timestamp"] = str(int(time.time()*1000))

                    yield scrapy.Request(url=url, method="post",callback=self.shop_goods, body=data,headers=headers,meta={"vender_id":vender_id},dont_filter=True)
        else:
            self.try_again(response)
    def shop_goods(self,response):
        meta = response.meta
        vender_id = meta.get("vender_id")

        match = re.search('"code":200',response.text)
        if match:
            item_s = GmWorkItem()
            item_s["key"] = vender_id
            item_s["pipeline_level"] = "goods"
            item_s["source_code"] = response.text
            yield item_s
            data_json = json.loads(response.text)
            data = data_json.get("data")
            totalCount = data.get("totalCount",0)#页数
            skuList = data.get("skuList",[])
            for i in skuList:
                commentNum = i.get("commentNum")
                goodComment = i.get("goodComment")
                imageUrl = i.get("imageUrl")
                promoStatus = i.get("promoStatus")
                skuId = i.get("skuId")
                skuName = i.get("skuName")
                # spuId = i.get("spuId")
                item = GmWorkItem()
                item["vender_id"] = vender_id
                item["total_num"] = totalCount
                item["comment_num"] = commentNum
                item["comment_score"] = goodComment
                item["img_url"] = imageUrl
                item["promo_statu"] = promoStatus
                item["goods_id"] = skuId
                item["goods_name"] = skuName
                # item["spuId"] = spuId
                yield item


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

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
pragma: no-cache
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
        else:
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Content-Type: application/json
Host: color.jd.id
Origin: https://m.jd.id
Referer: https://m.jd.id/shop/47986.html.html
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-site
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'''
        return headers_todict(headers)
