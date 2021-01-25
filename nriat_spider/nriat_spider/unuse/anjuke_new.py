# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
import json


class AnjukeNewSpider(RedisSpider):
    name = 'anjuke_new'
    allowed_domains = ['anjuke.com']
    start_urls = ['https://m.anjuke.com']
    redis_key = "anjuke_new:start_url"
    custom_settings = {"CONCURRENT_REQUESTS":2,"CHANGE_IP_NUM":50,"SCHEDULER_QUEUE_CLASS": 'scrapy_redis.queue.FifoQueue'}
    file_name = r"W:\scrapy_xc\anjuke\{infolist}[ID,名称,代号].txt"

    def start_requests(self):
        f = open(self.file_name, "r", encoding="utf-8")
        for i in f:
            cid = i.strip().split(",")[0]
            name = i.strip().split(",")[1]
            city = i.strip().split(",")[2]
            # cid = "18"
            # name = "杭州"
            # city = "hz"
            num = 1
            Referer = "https://m.anjuke.com/{}/loupan/all/".format(city)
            headers = self.get_headers(1)
            headers["Referer"] = Referer
            url = "https://m.anjuke.com/xinfang/api/loupan/list/?args=%7B%22cid%22:{},%22page%22:{},%22pageSize%22:20,%22args%22:%7B%7D,%22commerce%22:0,%22commerce_type%22:0,%22seoPage%22:null%7D&history_url=https:%2F%2Fm.anjuke.com%2F{}%2Floupan%2Fall%2F".format(
                cid, num, city)
            yield scrapy.Request(url=url, method="GET",callback=self.sort_all, headers=headers,meta={"first":True,"cid":cid,"name":name,"city":city})

    def sort_all(self,response):
        youxiao = re.search('(result)',response.text)
        first = response.meta.get("first")
        cid = response.meta.get("cid")
        name = response.meta.get("name")
        city = response.meta.get("city")
        url = response.request.url
        if youxiao:
            try:
                json_data = json.loads(response.text)
                result = json_data.get("result")
                total = result.get("total")
                rows = result.get("rows",[])
                for i in rows:
                    loupan_id = i.get("loupan_id")
                    new_price_value = i.get("new_price_value")
                    item = GmWorkItem()
                    item["cid"] = cid
                    item["name"] = name
                    item["city"] = city
                    item["loupan_id"] = loupan_id
                    item["new_price_value"] = new_price_value
                    yield item
                if first and int(total):
                    page_num = int(int(total)/20)+1 if int(total)%20 else int(int(total)/20)
                    Referer = "https://m.anjuke.com/{}/loupan/all/".format(city)
                    headers = self.get_headers(1)
                    headers["Referer"] = Referer
                    for i in range(2,page_num+1):
                        num = i
                        url = "https://m.anjuke.com/xinfang/api/loupan/list/?args=%7B%22cid%22:{},%22page%22:{},%22pageSize%22:20,%22args%22:%7B%7D,%22commerce%22:0,%22commerce_type%22:0,%22seoPage%22:null%7D&history_url=https:%2F%2Fm.anjuke.com%2F{}%2Floupan%2Fall%2F".format(
                            cid, num, city)
                        yield scrapy.Request(url=url, method="GET", callback=self.sort_all, headers=headers,
                                             meta={"cid": cid, "name": name, "city": city})
            except Exception as e:#有问题
                print(e)
                try_result = self.try_again(response, url=url)
                yield try_result
        else:
            try_result = self.try_again(response, url=url)
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
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''Host: m.anjuke.com
Connection: keep-alive
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)
