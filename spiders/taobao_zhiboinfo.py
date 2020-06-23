# -*- coding: utf-8 -*-
import scrapy
from nriat_spider.items import GmWorkItem
import json
from scrapy_redis.spiders import RedisSpider
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class SmtGoodsSpider(RedisSpider):
    name = 'taobao_zhiboinfo'
    allowed_domains = ['taobao.com']
    start_urls = ['https://h5.m.taobao.com']
    redis_key = "taobao_zhiboinfo:start_url"
    seeds_file = r"X:\数据库\淘宝直播\taobao_id增加.txt"
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 20,
        'nriat_spider.middlewares.TaobaoZhiboDownloaderMiddleware': 21,},
                       "CONCURRENT_REQUESTS":1,
                       "CHANGE_IP_NUM":400
                       }
    error_key = "taobao_zhiboinfo:error_url"


    def start_requests(self):
        yield scrapy.Request(url="https://www.baidu.com",dont_filter=True)

    def parse(self,response):
        for i in self.from_file(self.seeds_file):
            sellerid = i.strip()
            url = "https://{}.taobao.com".format(sellerid)
            meta = {"seller_id":sellerid}
            yield scrapy.Request(url=url,callback=self.get_detail,method="GET",meta=meta)

    def get_detail(self, response):
        seller_id = response.meta.get("seller_id")
        youxiao = re.search("(SUCCESS::调用成功)",response.text)
        if youxiao:
            try:
                match = re.search(" mtopjsonp3\((.*)\)", response.text)
                if match:
                    json_str = match.group(1)
                    json_data = json.loads(json_str)
                    data = json_data.get("data")
                    anchorId = data.get("anchorId")
                    nick = data.get("nick")
                    relation = data.get("relation")
                    fansCount = relation.get("fansCount")
                    followTopCount = relation.get("followTopCount")
                    liveCount = relation.get("liveCount")
                    replays = data.get("replays")
                    info_list = []
                    viewer_totle = 0
                    for i in replays:
                        info_dict = dict()
                        liveId = i.get("liveId")
                        liveTime = i.get("liveTime")
                        roomTypeName = i.get("roomTypeName")
                        title = i.get("title")
                        viewerCount = i.get("viewerCount")
                        info_dict["liveId"] = liveId
                        info_dict["liveTime"] = liveTime
                        info_dict["roomTypeName"] = roomTypeName
                        info_dict["title"] = title
                        info_dict["viewerCount"] = viewerCount
                        info_list.append(info_dict)
                        viewer_totle+=int(viewerCount)
                    live_info = json.dumps(info_list)
                    item = GmWorkItem()
                    item["anchor_id"] = anchorId
                    item["nick"] = nick
                    item["fans_count"] = fansCount
                    item["follow_count"] = followTopCount
                    item["live_count"] = liveCount
                    item["viewer_totle"] = viewer_totle
                    item["live_info"] = live_info
                    yield item
            except Exception as e:
                print(e)
                try_result = self.try_again(response, seller_id=seller_id)
                yield try_result
        else:
            try_result = self.try_again(response, seller_id=seller_id)
            yield try_result

    def from_file(self,file_name):
        with open(file_name,"r",encoding="utf-8") as f:
            for i in f:
                yield i

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