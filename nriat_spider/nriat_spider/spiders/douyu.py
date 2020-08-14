# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import json

class DouyuSpider(RedisSpider):
    name = 'douyu_sort'
    allowed_domains = ['douyu.com']
    start_urls = ['']
    redis_key = "douyu_sort:start_url"


    def start_requests(self):
        url = "https://www.douyu.com/gapi/rkc/directory/mixList/0_0/1"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,meta={"first":True},dont_filter=True)

    def sort_all(self,response):
        match = re.search('success',response.text)
        first = response.meta.get("first")
        if match:
            headers = self.get_headers(1)
            json_data = json.loads(response.text)
            data = json_data.get("data")
            pgcnt = data.get("pgcnt")
            rl = data.get("rl")
            for i in rl:
                c2name = i.get("c2name")
                rid = i.get("rid")
                ol = i.get("ol")#热度
                url = "https://www.douyu.com/betard/{}".format(rid)
                yield scrapy.Request(url=url, method="GET", callback=self.middle, headers=headers, meta={"rid": rid,"c2name":c2name,"ol":ol})
            if first:
                for i in range(2,pgcnt+1):
                    url = "https://www.douyu.com/gapi/rkc/directory/mixList/0_0/{}".format(i)
                    yield scrapy.Request(url=url, method="GET", callback=self.sort_all, headers=headers,dont_filter=True)
        else:
            try_result = self.try_again(response,url=response.url)
            yield try_result

    def middle(self,response):
        rid = response.meta.get("rid")
        c2name = response.meta.get("c2name")
        ol = response.meta.get("ol")

        match = re.search('up_id',response.text)
        if match:
            headers = self.get_headers(1)
            json_data = json.loads(response.text)
            room = json_data.get("room")
            up_id = room.get("up_id")
            url = "https://v.douyu.com/author/{}".format(up_id)
            yield scrapy.Request(url=url, method="GET", callback=self.dedail_data, headers=headers, meta={"up_id": up_id,"rid":rid,"c2name":c2name,"ol":ol})
        else:
            try_result = self.try_again(response,url=response.url)
            yield try_result

    def dedail_data(self,response):
        up_id = response.meta.get("up_id")
        rid = response.meta.get("rid")
        c2name = response.meta.get("c2name")
        ol = response.meta.get("ol")
        match = re.search('upId|roomId',response.text)
        if match:
            name = ""
            video = ""
            plays = ""
            fans = ""
            name_match = re.search('name: "([^"]*)"',response.text)
            if name_match:
                name = name_match.group(1)
            try:
                name = name.encode('utf-8').decode('unicode_escape')
            except Exception as e:
                pass
            video_match = re.search("upNum: '([^']*)'",response.text)
            if video_match:
                video = video_match.group(1)
            plays_match = re.search("playCount: '([^']*)'",response.text)
            if plays_match:
                plays = plays_match.group(1)
            fans_match = re.search("subscribeNum: '([^']*)'",response.text)
            if fans_match:
                fans = fans_match.group(1)
            item = GmWorkItem()
            item["up_id"] = up_id
            item["rid"] = rid
            item["c2name"] = c2name
            item["ol"] = ol
            item["name"] = name
            item["video"] = video
            item["plays"] = plays
            item["fans"] = fans
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
