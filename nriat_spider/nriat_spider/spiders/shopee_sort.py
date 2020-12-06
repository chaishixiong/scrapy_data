# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import json
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class ShopeeSpider(RedisSpider):
    name = 'shopee_sort'
    allowed_domains = ['shopee.com.my']
    start_urls = ['https://shopee.com.my/all_categories']
    redis_key = "shopee_sort:start_url"
    error_key = "shopee_sort:error_url"

    def start_requests(self):
        url = "https://shopee.com.my/api/v2/category_list/get_all"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        youxiao = re.search('("data")',response.text)
        key = "sort"
        if response.status == 200 and youxiao:
            item_s = GmWorkItem()
            item_s["key"] = key
            item_s["source_code"] = response.text
            yield item_s
            json_data = json.loads(response.text)
            data = json_data.get("data")
            for i in data:
                main = i.get("main")
                catid = main.get("catid")
                name = main.get("name")
                sub = i.get("sub")
                for j in sub:
                    sub_sub = j.get("sub_sub")
                    catid_sub = j.get("catid")
                    name_sub = j.get("name")
                    if sub_sub:
                        for x in sub_sub:
                            name_sub2 = x.get("display_name")
                            catid_sub2 = x.get("catid")
                            item = GmWorkItem()
                            item["catid"] = catid
                            item["category"] = None
                            item["catid_sub"] = catid_sub
                            item["category1"] = name_sub
                            item["catid_sub2"] = catid_sub2
                            item["category2"] = name_sub2
                            yield item
                    else:
                        item = GmWorkItem()
                        item["catid"] = catid
                        item["category"] = name
                        item["catid_sub"] = catid_sub
                        item["category1"] = name_sub
                        item["catid_sub2"] = ""
                        item["category2"] = ""
                        yield item

        else:
            yield self.try_again(response,key=key)


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
            # item_e = GmWorkItem()
            # item_e["error_id"] = 1
            # for i in kwargs:
            #     item_e[i] = kwargs[i]
            # return item_e

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''accept: */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
referer: https://shopee.com.my/all_categories
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.16 Safari/537.36
x-api-source: pc
x-requested-with: XMLHttpRequest'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)
