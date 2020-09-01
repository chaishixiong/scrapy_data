# -*- coding: utf-8 -*-
import scrapy
from nriat_spider.items import GmWorkItem
import re
from scrapy_redis.spiders import RedisSpider
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class SmtGoodsSpider(RedisSpider):
    goods_num = 0
    name = 'taobao_goods'
    allowed_domains = ['']
    start_urls = ['https://item.taobao.com/']
    redis_key = "taobao_goods:start_url"
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        "DOWNLOAD_DELAY":0.2,
    "DOWNLOADER_MIDDLEWARES" : {'nriat_spider.middlewares.TaobaoGoodsDownloaderMiddleware': 20,
        'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,},
        "CHANGE_IP_NUM":1000
    }
    error_key = "taobao_goods:error_url"

    def make_requests_from_url(self, goods_id):
        goods_id = goods_id.strip()
        url = "https://item.taobao.com/{}".format(goods_id)
        meta = {"goods_id":goods_id}
        return scrapy.Request(url=url,callback=self.get_detail,method="GET",meta=meta)

    def get_detail(self, response):

        if "调用成功" in response.text:
            item_s = GmWorkItem()
            item_s["source_code"] = response.text
            yield item_s
            match = re.search('"itemId":"([0-9]*)',response.text)
            goods_id = ""
            if match:
                goods_id= match.group(1)
            item = GmWorkItem()
            item["goods_id"]=goods_id
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