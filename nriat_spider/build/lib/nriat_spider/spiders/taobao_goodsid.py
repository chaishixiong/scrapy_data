# -*- coding: utf-8 -*-
import scrapy
from nriat_spider.items import GmWorkItem
import json
from scrapy_redis.spiders import RedisSpider
import re
import redis
from json.decoder import JSONDecodeError

class SmtGoodsSpider(RedisSpider):
    name = 'taobao_goodsid'
    allowed_domains = ['taobao.com']
    start_urls = ['https://h5.m.taobao.com']
    redis_key = "taobao_goodsid:start_url"
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 20,
        'nriat_spider.middlewares.TaobaoZhiboDownloaderMiddleware': 21,},
                       "CONCURRENT_REQUESTS":1}
    server1 = redis.Redis(host='192.168.0.226', port=5208, decode_responses=True)


    def make_requests_from_url(self, url):
        #这里还要将id和开始和结束的标记传进来，往后续传递，scrapy的有限集要先进先出
        data = url.split(":")
        live_id = data[0]
        seller_id = data[1]
        url = "https://{}.taobao.com".format(live_id)
        meta = {"live_id": live_id,"seller_id":seller_id}
        return scrapy.Request(url=url, callback=self.get_detail, method="GET", meta=meta)


    def get_detail(self, response):
        seller_id = response.meta.get("seller_id")
        youxiao = re.search("(SUCCESS::调用成功)",response.text)
        if youxiao:
            match = re.search(" mtopjsonp4\((.*)\)", response.text)
            if match:
                json_str = match.group(1)
                try:
                    json_data = json.loads(json_str)
                except JSONDecodeError as e:
                    json_data = {}
                    print(e)
                data = json_data.get("data",{})
                itemList = data.get("itemList",[])
                for item in itemList:
                    goodsIndex = item.get("goodsIndex")
                    goodsList = item.get("goodsList",[])
                    for goods in goodsList:
                        extendVal = goods.get("extendVal",{})
                        anchorId = extendVal.get("anchorId")
                        categoryLevelLeaf = extendVal.get("categoryLevelLeaf")
                        categoryLevelLeafName = extendVal.get("categoryLevelLeafName")
                        categoryLevelOne = extendVal.get("categoryLevelOne")
                        categoryLevelOneName = extendVal.get("categoryLevelOneName")

                        buyCount = goods.get("buyCount")
                        itemId = goods.get("itemId")
                        itemName = goods.get("itemName")
                        itemPic = goods.get("itemPic")
                        itemPrice = goods.get("itemPrice")
                        liveId = goods.get("liveId")
                        sellerId = goods.get("sellerId")

                        item = GmWorkItem()
                        item["anchor_id"] = anchorId
                        item["goods_index"] = goodsIndex
                        item["catid_sub"] = categoryLevelLeaf
                        item["category1"] = categoryLevelLeafName
                        item["catid"] = categoryLevelOne
                        item["category"] = categoryLevelOneName
                        item["sales_num"] = buyCount
                        item["goods_id"] = itemId
                        item["goods_name"] = itemName
                        item["goods_url"] = itemPic
                        item["price"] = itemPrice
                        item["live_id"] = liveId
                        item["seller_id"] = sellerId
                        yield item
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