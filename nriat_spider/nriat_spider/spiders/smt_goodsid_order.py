# -*- coding: utf-8 -*-
import scrapy
from nriat_spider.items import GmWorkItem
import json
from scrapy_redis.spiders import RedisSpider


class SmtGoodsSpider(RedisSpider):
    goods_num = 0
    name = 'smt_goodsid_order'
    allowed_domains = ['aliexpress.com']
    start_urls = ['http://m.aliexpress.com']
    redis_key = "smt_goodsid_order:start_url"
    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
    "DOWNLOADER_MIDDLEWARES" : {'nriat_spider.middlewares.SmtPrameDownloaderMiddleware': 20,
        'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,},
        "CHANGE_IP_NUM":400,
        "SCHEDULER_QUEUE_CLASS" : 'scrapy_redis.queue.LifoQueue'
        # "DOWNLOAD_DELAY" : 20,
    }
    # seeds_file = r"X:\数据库\速卖通\{1_1_速卖通_店铺信息}[店铺ID,卖家ID].txt"
    seeds_file = r"W:\scrapy_xc\smt_goodsid_order-error_合并.txt"

    def start_requests(self):
        yield scrapy.Request(url="https://www.baidu.com",dont_filter=True)

    def parse(self,response):
        for i in self.from_file(self.seeds_file):
            i = i.strip()
            num = 1
            field_num = i.count(",")
            if field_num == 2:
                num = i.split(",")[2]
            if "," in i:
                shop_id = i.split(",")[0]

                seller_id = i.split(",")[1]
                url = "https://{}.aliexpress.com".format(shop_id)
                meta = {"page_num":num,"shop_id":shop_id,"seller_id":seller_id}

                yield scrapy.Request(url=url,callback=self.get_detail,method="GET",meta=meta)

    def get_detail(self, response):
        meta = response.meta
        totle_num = meta.get("totle_num")
        if totle_num:
            totle_num = int(totle_num)
        page_num = int(meta.get("page_num"))
        shop_id = meta.get("shop_id")
        seller_id = meta.get("seller_id")

        judge = 0
        try:
            json_str = json.loads(response.text)
            data = json_str.get("data")
            if not totle_num:
                totle = data.get("total")
                totle_num = int(totle / 20)+1 if totle % 20 else int(totle / 20)
            ret = data.get("ret")
            for i in ret:
                item = GmWorkItem()
                id = i.get("id")
                orders = i.get("orders")
                salePrice = i.get("salePrice")
                maxPrice = salePrice.get("maxPrice")
                minPrice = salePrice.get("minPrice")
                pcDetailUrl = i.get("pcDetailUrl")
                subject = i.get("subject")
                averageStar = i.get("averageStar")#评分
                feedbacks = i.get("feedbacks")#反馈数
                mediaId = i.get("mediaId")#媒体id
                image350Url = i.get("image350Url")#图片url
                tagResult = i.get("tagResult")#标签

                item["shop_id"] = shop_id
                item["seller_id"] = seller_id
                item["totle_num"] = totle_num
                item["id"] = id
                item["orders"] = orders
                item["max_price"] = maxPrice
                item["min_price"] = minPrice
                item["goods_url"] = pcDetailUrl
                item["average_score"] = averageStar
                item["goods_name"] = subject
                item["comment_num"] = feedbacks
                item["media_id"] = mediaId
                item["img_url"] = image350Url
                item["tag"] = tagResult
                yield item

                if orders == 0:
                    judge = 1
            item_s = GmWorkItem()
            item_s["shop_id"] = shop_id
            item_s["source_code"] = json_str
            yield item_s

            if page_num >= totle_num or len(ret) < 20:
                judge = 1

            if judge == 0:
                page_num += 1
                url = "https://{}.aliexpress.com/{}".format(shop_id,page_num)
                meta = {"totle_num":totle_num,"page_num": page_num, "shop_id": shop_id, "seller_id": seller_id}
                yield scrapy.Request(url=url, callback=self.get_detail, method="GET",meta=meta)
        except Exception as e:
            try_result = self.try_again(response, shop_id,seller_id,page_num)
            yield try_result

    def from_file(self,file_name):
        with open(file_name,"r",encoding="utf-8") as f:
            for i in f:
                yield i

    def try_again(self,rsp,shop_id,seller_id,page_num):
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
            item_e["shop_id"] = shop_id
            item_e["seller_id"] = seller_id
            item_e["page_num"] = page_num
            return item_e