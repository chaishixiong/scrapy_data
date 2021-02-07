# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re,json
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class SharesSpider(RedisSpider):
    name = 'shares_zjlist'
    allowed_domains = ['eastmoney.com']
    start_urls = ['http://push2.eastmoney.com']
    redis_key = "shares_zjlist:start_url"
    custom_settings = {"DOWNLOAD_DELAY":4}
    error_key = "shares_zjlist:error_url"

    def start_requests(self):
        url = "http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112309261632244537723_1610434239236&fid=f174&po=1&pz=50&pn={}&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=b%3ABK0172".format(1)
        #东方财富区域资金流动浙江板块股票列表
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",headers=headers,meta={"first":True})

    def parse(self, response):
        youxiao = re.search("total",response.text)
        first = response.meta.get("first")
        headers = self.get_headers(1)
        if youxiao:
            match = re.search("jQuery112309261632244537723_1610434239236\(([\s\S]+)\)",response.text)
            if match:
                json_str = match.group(1)
                try:
                    json_data = json.loads(json_str)
                except:
                    json_data = {}
                    try_result = self.try_again(response)
                    yield try_result
                if json_data:
                    data = json_data.get("data",{})
                    total = data.get("total",0)
                    if first and total > 50:
                        num = int(total/50)+1 if total%50 else int(total/50)
                        for i in range(2,num+1):
                            url = "http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112309261632244537723_1610434239236&fid=f174&po=1&pz=50&pn={}&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=b%3ABK0172".format(i)
                            yield scrapy.Request(url=url, method="GET", headers=headers)
                    diff = data.get("diff",[])
                    for i in diff:
                        id = i.get("f12")
                        name = i.get("f14")
                        item = GmWorkItem()
                        item["id"] = id
                        item["name"] = name
                        yield item
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

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: push2.eastmoney.com
Referer: http://data.eastmoney.com/
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'''
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
