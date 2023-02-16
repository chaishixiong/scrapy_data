# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re,json
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
from urllib.parse import quote
class WenzhouTeachSpider(RedisSpider):
    name = 'wenzhou_teach'
    allowed_domains = []
    start_urls = []
    redis_key = "wenzhou_teach:start_url"
    custom_settings = {"CONCURRENT_REQUESTS":2,"CHANGE_IP_NUM":100}
    # server = redis.Redis(host='192.168.0.226', port=5208, decode_responses=True)
    error_key = "xiecheng:error_url"
    def start_requests(self):
        stype = ["幼儿园","小学","中学","高等院校","职业学校","特殊教育学校","驾校","培训机构"]
        for type in stype:
            name = quote(type)
            url = "https://services.wzmap.gov.cn/server/rest/services/TDT/ZhuanTiSJ/MapServer/7/query?f=json&returnIdsOnly=true&returnCountOnly=true&orderByFields=tdt.DBO.%E6%95%99%E8%82%B2.HOTSPOT%20DESC&spatialRel=esriSpatialRelIntersects&where=tdt.DBO.%E6%95%99%E8%82%B2.TAG%20LIKE%20%27%25{}%25%27%20%20".format(name)
            headers = self.get_headers(1)
            yield scrapy.Request(url=url,method="GET",headers=headers,dont_filter=True,callback=self.get_num,meta={"type":type})


    def get_num(self,response):
        youxiao = re.search("count",response.text)
        type = response.meta.get("type")
        if youxiao:
            try:
                data_json = json.loads(response.text)
                count = data_json.get("count")
                for num in range(0,int(count),20):
                    name = quote(type)
                    url = "https://services.wzmap.gov.cn/server/rest/services/TDT/ZhuanTiSJ/MapServer/7/query?f=json&resultOffset={}&resultRecordCount=20&where=tdt.DBO.%E6%95%99%E8%82%B2.TAG%20LIKE%20%27%25{}%25%27%20%20&orderByFields=tdt.DBO.%E6%95%99%E8%82%B2.HOTSPOT%20DESC&outFields=*&spatialRel=esriSpatialRelIntersects".format(num,name)
                    headers = self.get_headers(1)
                    yield scrapy.Request(url=url,method="GET",headers=headers,dont_filter=True,meta={"type":type})

            except:
                try_result = self.try_again(response)
                yield try_result
        else:
            try_result = self.try_again(response)
            yield try_result

    def parse(self, response):
        youxiao = re.search("features",response.text)
        type = response.meta.get("type")
        if youxiao:
            try:
                data_json = json.loads(response.text)
                features = data_json.get("features")
                for i in features:
                    attributes = i.get("attributes")
                    name = attributes.get("tdt.DBO.教育.NAME")
                    address = attributes.get("tdt.DBO.教育.ADDRESS")
                    labelx = attributes.get("tdt.DBO.教育.LABELX")
                    labely = attributes.get("tdt.DBO.教育.LABELY")
                    county = attributes.get("tdt.DBO.教育.COUNTY")
                    town = attributes.get("tdt.DBO.教育.TOWN")
                    summary = attributes.get("tdt.DBO.教育.SUMMARY")
                    item = GmWorkItem()
                    item["name"]=name
                    item["address"]=address
                    item["labelx"]=labelx
                    item["labely"]=labely
                    item["county"]=county
                    item["town"]=town
                    item["summary"]=summary
                    item["type"]=type
                    yield item
            except:
                try_result = self.try_again(response)
                yield try_result
        else:
            try_result = self.try_again(response)
            yield try_result


    def try_again(self,rsp):
        print("错误了")
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
                self.server.lpush(self.error_key,data)
            except Exception as e:
                print(e)
            # item_e = GmWorkItem()
            # item_e["error_id"] = 1
            # for i in kwargs:
            #     item_e[i] = kwargs[i]
            # return item_e

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'''
        else:
            headers = '''accept: application/json
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
content-type: application/json;charset=UTF-8
origin: https://hotels.ctrip.com
pragma: no-cache
sec-fetch-mode: cors
sec-fetch-site: same-site
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36
Host: m.ctrip.com
'''
        return headers_todict(headers)
