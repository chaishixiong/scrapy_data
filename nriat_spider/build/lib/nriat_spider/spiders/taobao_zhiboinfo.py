# -*- coding: utf-8 -*-
import scrapy
from nriat_spider.items import GmWorkItem
import json
from scrapy_redis.spiders import RedisSpider
import re
import redis

class SmtGoodsSpider(RedisSpider):
    name = 'taobao_zhiboinfo'
    allowed_domains = ['taobao.com']
    start_urls = ['https://h5.m.taobao.com']
    redis_key = "taobao_zhiboinfo:start_url"
    seeds_file = r"X:\数据库\淘宝直播\taobao_id.txt"
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 20,
        'nriat_spider.middlewares.TaobaoZhiboDownloaderMiddleware': 21,},
                       "CONCURRENT_REQUESTS":1}
    server1 = redis.Redis(host='192.168.0.226', port=5208, decode_responses=True)
    # server1 = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True,password="nriat.123456")
    next_seed = "taobao_goodsid:start_url"


    def start_requests(self):
        yield scrapy.Request(url="https://www.baidu.com",dont_filter=True)

    def parse(self,response):
        for i in self.from_file(self.seeds_file):
            sellerid = i.strip()
            url = "https://{}.taobao.com".format(sellerid)
            meta = {"seller_id":sellerid}
            yield scrapy.Request(url=url,callback=self.get_detail,method="GET",meta=meta,dont_filter=True)

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

                    ##y预告的部分 之后再做
                    # prevueVideos = data.get("prevueVideos")
                    # for video in prevueVideos:
                    #     title = video.get("title")
                    #     prevueBegainTime = video.get("prevueBegainTime")#预告时间
                    #     liveId = video.get("liveId")#预告场次id
                    #     # self.server1.zadd("","")#将时间和场次id加入到队列中 后续根据当前时间取出场次id跑场次id取goodsid的脚本
                    ##
                    replays = data.get("replays")#这个是过去十场直播数据
                    for i in replays:
                        liveId = i.get("liveId")
                        liveTime = i.get("liveTime")
                        roomTypeName = i.get("roomTypeName")
                        title = i.get("title")
                        viewerCount = i.get("viewerCount")
                        item = GmWorkItem()
                        item["anchor_id"] = anchorId
                        item["nick"] = nick
                        item["fans_count"] = fansCount
                        item["follow_count"] = followTopCount
                        item["live_count"] = liveCount
                        item["live_id"] = liveId
                        item["live_time"] = liveTime
                        item["room_name"] = roomTypeName
                        item["title"] = title
                        item["viewer_count"] = viewerCount
                        yield item
                        self.server1.sadd(self.next_seed,"{}:{}".format(liveId,anchorId))
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
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e