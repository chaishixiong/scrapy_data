# # -*- coding: utf-8 -*-
# import scrapy
# from scrapy_redis.spiders import RedisSpider
# from nriat_spider.items import GmWorkItem
# from tools.tools_r.header_tool import headers_todict
# import re
# import json
# from scrapy.utils.reqser import request_to_dict
# from scrapy_redis import picklecompat
#
# class BaiduxinyongSpider(RedisSpider):
#     name = 'baiduxinyong_id'
#     allowed_domains = ['']
#     start_urls = ['https://aiqicha.baidu.com/']
#     redis_key = "baiduxinyong_id:start_url"
#     error_key = "baiduxinyong_id:error_key"
#     custom_settings = {}
#
#     def make_requests_from_url(self, url):
#         headers = self.get_headers(1)
#         id = url.replace("http://","")
#         url_new = "https://aiqicha.baidu.com/s?q={}&t=0&fl=1&castk=LTE%3D".format(id)
#         return scrapy.Request(url=url_new, method="GET", headers=headers, meta={"id": id}, dont_filter=True)#这里需要return
#
#
#     def parse(self, response):
#         meta = response.meta
#         id = meta.get("id")
#         youxiao = re.search('"resultList":\[',response.text)
#         if youxiao:
#             try:
#                 company = re.findall('"entName":"(.*?)"', response.text)[0]
#                 company = company.encode('latin-1').decode('unicode_escape')
#                 # print(company)
#             except:
#                 company = ''
#
#             try:
#                 legal_person = re.findall('"legalPerson":"(.*?)","tags"', response.text)[0]
#                 legal_person = legal_person.encode().decode('unicode_escape')
#                 # print(legal_person)
#             except:
#                 legal_person = ''
#
#             try:
#                 area = re.findall('"titleDomicile":"(.*?)"', response.text)[0]
#                 area = area.encode().decode('unicode_escape')
#                 # print(area)
#             except:
#                 area = ''
#             item111 = ','.join([company, id, legal_person, area])
#             print(item111)
#
#             item = GmWorkItem(company=company, id=id, legal_person=legal_person, area=area)
#             yield item
#
#         else:
#             print("{}错误了".format(id))
#             try_result = self.try_again(response)
#             yield try_result
#
#     def try_again(self,rsp):
#         max_num = 5
#         meta = rsp.meta
#         try_num = meta.get("try_num",0)
#         if try_num < max_num:
#             try_num += 1
#             request = rsp.request
#             request.dont_filter = True
#             request.meta["try_num"] = try_num
#             return request
#         else:
#             request = rsp.request
#             request.meta["try_num"] = 0
#             obj = request_to_dict(request, self)
#             data = picklecompat.dumps(obj)
#             try:
#                 self.server.lpush(self.error_key, data)
#             except Exception as e:
#                 print(e)
#     def get_headers(self,type = 1):
#         if type == 1:
#             headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
#             accept-encoding: gzip, deflate, br
#             accept-language: zh-CN,zh;q=0.9
#             upgrade-insecure-requests: 1
#             user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'''
#         else:
#             headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
#             accept-encoding: gzip, deflate, br
#             accept-language: zh-CN,zh;q=0.9
#             upgrade-insecure-requests: 1
#             user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'''
#         return headers_todict(headers)
#


# -*- coding: utf-8 -*-

import scrapy
from scrapy_redis.spiders import RedisSpider
from ..items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re,os
import json
import redis
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class BaiduxinyongSpider(RedisSpider):
    name = 'baiduxinyong_id'
    # allowed_domains = ['']
    # start_urls = ['https://aiqicha.baidu.com/']
    # custom_settings = {"REDIRECT_ENABLED": True, "CHANGE_IP_NUM": 200, "CONCURRENT_REQUESTS": 4}
    redis_key = "baiduxinyong_id:start_url"
    error_key = "baiduxinyong_id:error_url"
    custom_settings = {
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'REDIS_URL': 'redis://192.168.0.230:5208/4',
        'SCHEDULER_PERSIST': True,
        "CHANGE_IP_NUM": 200, "CONCURRENT_REQUESTS": 4
    }

    def start_requests(self):
        with open('X:\数据库\工商地址库\亚马逊\company_id.txt_去重.txt','r',encoding='utf-8') as f:
            for i in f:
                i = i.replace('\n','')
                url_new = "https://aiqicha.baidu.com/s?q={}&t=0&fl=1&castk=LTE%3D".format(i)
                headers = self.get_headers(1)
                yield scrapy.Request(url=url_new,method="GET",callback=self.parse,headers=headers,dont_filter=True,meta={"id": i})

    def parse(self, response):
        meta = response.meta
        id = meta.get("id")
        youxiao = re.search('"resultList":\[',response.text)
        if youxiao:
            try:
                company = re.findall('"entName":"(.*?)"', response.text)[0]
                company = company.encode('latin-1').decode('unicode_escape')
                # print(company)
            except:
                company = ''

            # print(i)
            try:
                legal_person = re.findall('"legalPerson":"(.*?)","tags"', response.text)[0]
                legal_person = legal_person.encode().decode('unicode_escape')
                # print(legal_person)
            except:
                legal_person = ''

            try:
                area = re.findall('"titleDomicile":"(.*?)"', response.text)[0]
                area = area.encode().decode('unicode_escape')
                # print(area)
            except:
                area = ''
            item111 = ','.join([company, id, legal_person, area])
            # print(item111)

            item = GmWorkItem(company=company, id=id, legal_person=legal_person, area=area)
            yield item

        else:
            # print("{}错误了".format(id))
            # self.huan_ip()
            try_result = self.try_again(response, id=id)
            yield try_result

    def try_again(self,rsp,**kwargs):
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
                self.server.lpush(self.error_key, data)
            except Exception as e:
                print(e)

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
            accept-encoding: gzip, deflate, br
            accept-language: zh-CN,zh;q=0.9
            upgrade-insecure-requests: 1
            user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
            accept-encoding: gzip, deflate, br
            accept-language: zh-CN,zh;q=0.9
            upgrade-insecure-requests: 1
            user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)
