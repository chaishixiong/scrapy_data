# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
import json


class GaodeSpider(RedisSpider):
    name = 'gaode'
    allowed_domains = ['amap.com']
    start_urls = ['']
    redis_key = "gaode:start_url"
    headers = headers_todict('''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36''')
    error_key = "alibabgj_shop:error_key"
    ak= "91d21af63da4bd5b63a42ae486376000"


    def make_requests_from_url(self, i):
            data = i.strip().split(",")
            num = data[0]
            lan = data[1]
            lat = data[2]
            url = "http://restapi.amap.com/v3/geocode/regeo?key={}&location={},{}&poitype=&radius=1000&extensions=base&batch=false&roadlevel=0".format(self.ak,lan,lat)
            meta = {"key":num}
            return scrapy.Request(url=url,method="GET",headers=self.headers,meta=meta)

    def parse(self, response):
        youxiao = re.search('"status":"1"',response.text)
        key = response.meta.get("key")
        if youxiao:
            text = response.text
            item_s = GmWorkItem()
            item_s["key"] = key
            item_s["source_code"] = text
            yield item_s
            data = json.loads(text)
            regeocode = data.get("regeocode",{})
            formatted_address = regeocode.get("formatted_address")
            item = GmWorkItem()
            item["key"] = key
            item["address"] = formatted_address
            yield item
        else:
            try_result = self.try_again(response,key)
            yield try_result


    def try_again(self,rsp,key):
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
