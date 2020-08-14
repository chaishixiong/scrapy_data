# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class AllegroSpider(RedisSpider):
    name = 'data_shua'
    allowed_domains = ['']
    start_urls = ['']
    redis_key = "data_shua:start_url"
    error_key = "data_shua:error_url"
    custom_settings = {"CHANGE_IP_NUM":20,"CONCURRENT_REQUESTS":1}

    def start_requests(self):
        url = "https://www.baidu.com"
        yield scrapy.Request(url=url,method="GET",headers=self.get_headers(2),callback=self.sort_all,dont_filter=True)

    def sort_all(self,response):
        if response.status == 200:
            with open('X:\数据库\临时\data_id.txt',"r",encoding="utf-8") as f:
                for i in f:
                    url = "http://data.wz.zjzwfw.gov.cn/jdop_front/detail/data.do?iid={}&searchString=".format(i.strip())
                    yield scrapy.Request(url=url, method="GET", headers=self.get_headers(1),callback=self.sort_all1, dont_filter=True)
        else:
            try_result = self.try_again(response,url=response.url)
            yield try_result

    def sort_all1(self,response):
        if response.status == 200 and "数据集" in response.text:
            item = GmWorkItem()
            item["shop_id"] = 1
            yield item
        else:
            try_result = self.try_again(response,url=response.url)
            yield try_result

    def try_again(self,rsp,**kwargs):
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
            headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Cookie: visited=1; JSESSIONID=A6E576B38D1D08EB87C7EF71B07FF1F2; ZJZWFWSESSIONID=8b1da8a4-dfd9-4d0c-ae8c-c461e975b1cc
Host: data.wz.zjzwfw.gov.cn
Pragma: no-cache
Referer: http://data.wz.zjzwfw.gov.cn/jdop_front/channal/data_public.do
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)

