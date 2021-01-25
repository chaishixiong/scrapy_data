# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
import redis


class AnjukeOldSpider(RedisSpider):
    name = 'anjuke_old'
    allowed_domains = ['anjuke.com']
    start_urls = ['https://m.anjuke.com']
    redis_key = "anjuke_old:start_url"
    custom_settings = {"CONCURRENT_REQUESTS":4,"CHANGE_IP_NUM":50,"SCHEDULER_QUEUE_CLASS": 'scrapy_redis.queue.FifoQueue'}
    file_name = r"X:\数据库\安居客\xc\{infolist}[ID,名称,代号,拼音].txt"
    # Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password="nriat.123456", max_connections=3)
    server = redis.Redis(host='192.168.0.226', port=5208, decode_responses=True)
    error_key = "anjuke_old:error_url"

    def start_requests(self):
        headers = self.get_headers(1)
        url = "https://www.baidu.com"
        yield scrapy.Request(url=url, method="GET",callback=self.seed_requests, headers=headers)

    def seed_requests(self, response):
        f = open(self.file_name, "r", encoding="utf-8")
        for i in f:
            data = i.strip().split(",")
            # cid = data[0]
            city = data[1]
            id_city = data[2]
            pinyin_city = data[3]
            headers = self.get_headers(1)
            url = "https://{}.anjuke.com/sale/".format(pinyin_city)
            meta ={"city":city,"id_city":id_city,"pinyin_city":pinyin_city}
            yield scrapy.Request(url=url, method="GET",callback=self.get_area, headers=headers,meta=meta)

    def get_area(self,response):
        url = response.request.url
        city = response.meta.get("city")
        id_city = response.meta.get("id_city")
        pinyin_city = response.meta.get("pinyin_city")
        area_name = response.meta.get("area_name")
        area_url = response.meta.get("area_url")
        not_first = response.meta.get("not_first")

        youxiao = re.search('(elems-l|houselist-mod-new)',response.text)
        if youxiao:
            headers = self.get_headers(1)
            # 获得区域
            if not area_name and "elems-l" in response.text:
                try:
                    area_list = response.css(".elems-l")[0].xpath("./a")
                except:
                    area_list = []
                for i in area_list:
                    area_name = i.xpath("./text()").get()
                    area_url = i.xpath("./@href").get()
                    if "周边" not in area_name:
                        meta = { "city": city, "id_city": id_city, "pinyin_city": pinyin_city,"area_name":area_name,"area_url":area_url}
                        yield scrapy.Request(url=area_url, method="GET", callback=self.get_area, headers=headers, meta=meta)
            else:
                # 分页
                if not not_first:
                    totle_num = 0
                    match = re.search('"found":(\d*)', response.text)
                    if match:
                        totle_num1 = match.group(1)
                        if totle_num1:
                            totle_num = int(totle_num1)
                    page_num = int(totle_num / 66) + 1 if totle_num % 66 else int(totle_num / 66)
                    page_num = 50 if page_num > 50 else page_num
                    for i in range(2, page_num + 1):
                        url_next = url+"p{}/".format(i)
                        meta = {"city": city, "id_city": id_city, "pinyin_city": pinyin_city,"area_name":area_name,"area_url":area_url, "not_first": True}
                        yield scrapy.Request(url=url_next, method="GET", callback=self.get_area, headers=headers,meta=meta)
                ##解析房屋
                goods_list = response.css(".house-title").xpath("./a")
                for i in goods_list:
                    house_url = i.xpath("./@href").get()
                    house_id = ""
                    match_id = re.search("view/([A\d]+)\?",house_url)
                    if match_id:
                        house_id = match_id.group(1)
                    item = GmWorkItem()
                    item["city"] = city
                    item["id_city"] = id_city
                    item["pinyin_city"] = pinyin_city
                    item["area_name"] = area_name
                    item["area_url"] = area_url
                    item["house_url"] = house_url
                    item["house_id"] = house_id
                    yield item
        else:
            print(url)
            try_result = self.try_again(response)
            if try_result:
                yield try_result


    def try_again(self,rsp,**kwargs):
        max_num = 10
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
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
pragma: no-cache
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        return headers_todict(headers)
