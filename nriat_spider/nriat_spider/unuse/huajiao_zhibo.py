# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
import json
import time
import random
import math

class HuajiaoSpider(RedisSpider):
    name = 'huajiao_zhibo'
    allowed_domains = ['huajiao.com']
    start_urls = ['']
    redis_key = "huajiao_zhibo:start_url"
    custom_settings = {'CONCURRENT_REQUESTS': 2,"CHANGE_IP_NUM": 100}

    def start_requests(self):
        time_new = str(int(time.time()*1000))
        random_num = random.random()*math.pow(10,14)
        random_str = str(int(random_num))
        headers = self.get_headers(1)
        for i in range(0, 300, 20):
            url = "https://webh.huajiao.com/live/listcategory?_callback=jQuery11020{0}_{1}&cateid=1000&offset={2}&nums=20&fmt=jsonp&_={1}".format(
                random_str, time_new, i)
            yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        match = re.search("jQuery11020\d{14}_\d{13}\((.*)\)", response.text)
        if "total" in response.text and match:
            text = match.group(1)
            headers = self.get_headers(2)
            json_data = json.loads(text)
            data = json_data.get("data")
            feeds = data.get("feeds")

            for i in feeds:
                author = i.get("author")
                uid = author.get("uid")
                nickname = author.get("nickname")
                signature = author.get("signature")
                feed = i.get("feed")
                labels = feed.get("labels")
                url = "https://www.huajiao.com/user/{}".format(uid)
                yield scrapy.Request(url=url, method="GET", callback=self.detail_data, headers=headers, meta={"uid": uid,"nickname":nickname,"signature":signature,"labels":labels})
        else:
            try_result = self.try_again(response,url=response.url)
            yield try_result

    def detail_data(self,response):
        uid = response.meta.get("uid")
        nickname = response.meta.get("nickname")
        signature = response.meta.get("signature")
        labels = response.meta.get("labels")
        match = re.search('handle',response.text)
        if match:
            info_list = response.css(".handle").xpath("./div/ul/li")
            gift_num = "0"
            getgift_num = "0"
            praise_num = "0"
            fans_num = "0"

            for i in info_list:
                name = i.xpath("./p/text()").get()
                value = i.xpath("./h4/text()").get()
                if "送礼" in name:
                    gift_num = value.strip()
                elif "收礼" in name:
                    getgift_num = value.strip()
                elif "赞" in name:
                    praise_num = value.strip()
                elif "粉丝" in name:
                    fans_num = value.strip()

            item = GmWorkItem()
            item["up_id"] = uid
            item["nick"] = nickname
            item["signature"] = signature
            item["labels"] = str(labels)
            item["gift_num"] = gift_num
            item["getgift_num"] = getgift_num
            item["ol"] = praise_num
            item["fans"] = fans_num
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
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Host: webh.huajiao.com
Pragma: no-cache
Referer: https://www.huajiao.com/category/1000
Sec-Fetch-Mode: no-cors
Sec-Fetch-Site: same-site
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
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
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
        return headers_todict(headers)
