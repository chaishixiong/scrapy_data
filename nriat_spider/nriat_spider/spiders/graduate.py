# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class GraduateSpider(RedisSpider):
    name = 'graduate'
    allowed_domains = ['yz.chsi.com.cn']
    start_urls = ['https://yz.chsi.com.cn/']
    redis_key = "graduate:start_url"
    error_key = "graduate:error_url"

    custom_settings = {"CONCURRENT_REQUESTS":2,"CHANGE_IP_NUM":100}

    def start_requests(self):
        headers = self.get_headers(1)
        dict_type = {"10":"学术型硕士","20":"专业学位硕士","30":"学术型博士","40":"专业学位博士"}
        for i,y in dict_type.items():
            data = "method=subCategoryMl&key={}".format(i)
            yield scrapy.FormRequest(url="https://yz.chsi.com.cn/zyk/specialityCategory.do",headers=headers,callback=
            self.sort_all,method="POST",body=data,meta={"type_1":y})
            

    def sort_all(self,response):
        request_url = response.request.url
        type_1 = response.meta.get("type_1")
        if response.status == 200:
            headers = self.get_headers(1)
            list_type2 = response.xpath("//li")
            for i in list_type2:
                name = i.xpath("./text()").get()
                id = i.xpath("./@id").get()
                meta = {"type_1":type_1,"type_2":name}
                data = "method=subCategoryMl&key={}".format(id)
                yield scrapy.FormRequest(url="https://yz.chsi.com.cn/zyk/specialityCategory.do",headers=headers,callback=
                self.sort_all1,method="POST",body=data,meta=meta)
                
        else:
            try_result = self.try_again(response,url=request_url)
            yield try_result

    def sort_all1(self,response):
        request_url = response.request.url
        type_1 = response.meta.get("type_1")
        type_2 = response.meta.get("type_2")
        if response.status == 200:
            headers = self.get_headers(1)
            list_type2 = response.xpath("//li")
            for i in list_type2:
                name = i.xpath("./text()").get()
                id = i.xpath("./@id").get()
                meta = {"type_1":type_1,"type_2":type_2,"type_3":name}
                data = "method=subCategoryXk&key={}".format(id)
                yield scrapy.FormRequest(url="https://yz.chsi.com.cn/zyk/specialityCategory.do",headers=headers,callback=
                self.sort_all2,method="POST",body=data,meta=meta)
                
        else:
            try_result = self.try_again(response,url=request_url)
            yield try_result

    def sort_all2(self,response):
        request_url = response.request.url
        type_1 = response.meta.get("type_1")
        type_2 = response.meta.get("type_2")
        type_3 = response.meta.get("type_3")
        if response.status == 200:
            headers = self.get_headers(1)
            list_type2 = response.xpath("//tr/td/a")
            for i in list_type2:
                name = i.xpath("./text()").get()
                if name:
                    name = name.strip()
                url = i.xpath("./@href").get()
                match = re.search("zydm=(\d+)&",url)
                if match:
                    id = match.group(1)
                else:
                    id = ""
                meta = {"type_1":type_1,"type_2":type_2,"type_3":type_3,"type_4":name,"id":id}
                url = "https://yz.chsi.com.cn"+url
                yield scrapy.Request(url=url,headers=headers,callback=self.parse,method="GET",meta=meta)
                
        else:
            try_result = self.try_again(response,url=request_url)
            yield try_result

    def parse(self,response):
        request_url = response.request.url
        type_1 = response.meta.get("type_1")
        type_2 = response.meta.get("type_2")
        type_3 = response.meta.get("type_3")
        type_4 = response.meta.get("type_4")
        id = response.meta.get("id")
        if response.status == 200:
            headers = self.get_headers(1)
            area = response.xpath("//div[@class='tab-item']/a")
            for i in area:
                name = i.xpath("./text()").get()
                if name:
                    name = name.strip()
                url = i.xpath("./@href").get()
                meta = {"type_1":type_1,"type_2":type_2,"type_3":type_3,"type_4":type_4,"id":id,"area":name}
                url = "https://yz.chsi.com.cn"+url
                yield scrapy.Request(url=url,headers=headers,callback=self.parse2,method="GET",meta=meta)
                
        else:
            try_result = self.try_again(response,url=request_url)
            yield try_result

    def parse2(self,response):
        request_url = response.request.url
        type_1 = response.meta.get("type_1")
        type_2 = response.meta.get("type_2")
        type_3 = response.meta.get("type_3")
        type_4 = response.meta.get("type_4")
        id = response.meta.get("id")
        area1 = response.meta.get("area")
        if response.status == 200:
            area = response.css(".clearfix").xpath("./li")
            for i in area:
                name = i.xpath("./@title").get()
                if name:
                    name = name.strip()
                item = GmWorkItem()
                item["type_1"] = type_1
                item["type_2"] = type_2
                item["type_3"] = type_3
                item["type_4"] = type_4
                item["id"] = id
                item["area"] = area1
                item["school"] = name
                yield item
        else:
            try_result = self.try_again(response,url=request_url)
            yield try_result

    def try_again(self,rsp,**kwargs):
        max_num = 20
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
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Host: yz.chsi.com.cn
Origin: https://yz.chsi.com.cn
Referer: https://yz.chsi.com.cn/zyk/
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36
X-Requested-With: XMLHttpRequest'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)
