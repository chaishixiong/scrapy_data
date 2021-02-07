# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re,json
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class SharesSpider(RedisSpider):
    name = 'shares_history'
    allowed_domains = ['sina.com.cn']
    start_urls = ['https://finance.sina.com.cn/']
    redis_key = "shares_history:start_url"
    custom_settings = {"DOWNLOAD_DELAY":3}
    error_key = "shares_history:error_url"

    def start_requests(self):
        headers = self.get_headers(1)
        with open(r"D:\scrapy_seed\shares_seed.txt","r",encoding="utf-8") as f:
            for i in f:
                id = i.strip()
                url = "https://finance.sina.com.cn/realstock/company/{}/houfuquan.js?d=2016-01-01".format(id)
                #新浪财经url
                yield scrapy.Request(url=url,method="GET",headers=headers,meta={"id":id})


    def parse(self, response):
        youxiao = re.search("total",response.text)
        id = response.meta.get("id")
        if youxiao:
            match = re.search("(\[[\s\S]+\])",response.text)
            if match:
                json_str = match.group(1)
                split_data = json_str.split(",")
                for i in split_data:
                    date_match = re.search("_(\d{4}_\d{2}_\d{2})",i)
                    price_match = re.search('"([\d\.]+)"',i)
                    if date_match and price_match:
                        date = date_match.group(1)
                        price = price_match.group(1)
                        item = GmWorkItem()
                        item["id"] = id
                        item["date"] = date
                        item["price"] = price
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

    def get_headers(self,type=1):
        if type == 1:
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: finance.sina.com.cn
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
