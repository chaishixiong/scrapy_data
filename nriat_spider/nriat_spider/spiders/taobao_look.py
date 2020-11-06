# -*- coding: utf-8 -*-
import scrapy
from nriat_spider.items import GmWorkItem
import re
from scrapy_redis.spiders import RedisSpider
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
import json,jsonpath


class TaobaoGoodSpider(RedisSpider):
    goods_num = 0
    name = 'taobao_look'
    allowed_domains = ['']
    start_urls = ['https://item.taobao.com/']
    redis_key = "taobao_look:start_url"
    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        # "DOWNLOAD_DELAY":0.1,
        "DOWNLOADER_MIDDLEWARES":{'nriat_spider.middlewares.TaobaoLookDownloaderMiddleware': 20,
        'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,},
        "CHANGE_IP_NUM":500
    }
    error_key = "taobao_look:error_url"

    def make_requests_from_url(self, data):
        data = data.strip().split(",")
        goods_id = data[0]
        seller_id = data[1]
        url = "https://item.taobao.com/{}".format(goods_id)
        meta = {"goods_id":goods_id,"seller_id":seller_id}
        return scrapy.Request(url=url,callback=self.get_detail,method="GET",meta=meta)

    def get_detail(self, response):
        if "调用成功" in response.text:
            item_s = GmWorkItem()
            item_s["source_code"] = response.text
            yield item_s
            match = re.search(" mtopjsonp3\((.*)\)", response.text)
            if match:
                json_str = match.group(1)
                try:
                    json_data = json.loads(json_str)
                except Exception as e:
                    json_data = {}
                data = json_data.get("data",{})
                result = data.get("result",[])
                for list_type in result:
                    itemList = list_type.get("itemList",[])
                    for i in itemList:
                        itemId = i.get("itemId")
                        sellerId = i.get("sellerId")
                        price = i.get("salePrice")
                        if not price:
                            price = i.get("price")
                        sold = i.get("sold")
                        name = i.get("name")
                        cid = i.get("categoryId")
                        score = i.get("score")
                        picUrl = i.get("picUrl")
                        item = GmWorkItem()
                        item["goods_id"] = itemId
                        item["seller_id"] = sellerId
                        item["price"] = price
                        item["sales_num"] = sold
                        item["goods_name"] = name
                        item["cid"] = cid
                        item["score"] = score
                        item["img_url"] = picUrl
                        yield item
        else:
            try_result = self.try_again(response)
            yield try_result

    def try_again(self,rsp):
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