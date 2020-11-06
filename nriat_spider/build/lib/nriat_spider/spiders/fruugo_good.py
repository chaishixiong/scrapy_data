# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class FruugoSpider(RedisSpider):
    name = 'fruugo_good'
    allowed_domains = ['fruugo.co.uk']
    start_urls = ['https://www.fruugo.co.uk']
    redis_key = "fruugo_good:start_url"
    custom_settings = {"REDIRECT_ENABLED":True,"CHANGE_IP_NUM":200,"CONCURRENT_REQUESTS":4}
    # file_name = r"X:\数据库\fruugo\fruugo_sort-data_合并.txt_去重.txt[F3].txt"
    error_key = "fruugo_good:error_url"

    # def start_requests(self):
    #     url = "https://www.baidu.com"
    #     headers = self.get_headers(1)
    #     yield scrapy.Request(url=url,callback=self.seed_process,method="GET",headers=headers,dont_filter=True)#
    #
    # def seed_process(self,response):
    #     headers = self.get_headers(1)
    #     if response.status == 200:
    #         for i in open(self.file_name,"r",encoding="utf-8"):
    #             url = i.strip()
    #             yield scrapy.Request(url=url, method="GET", headers=headers)

    def make_requests_from_url(self, i):
        url = i.strip()
        return scrapy.Request(url=url, method="GET", headers=self.get_headers(1))

    def parse(self, response):
        youxiao = re.search("(product-title|no longer available)",response.text)
        url_key = response.request.url
        if youxiao:
            item_s = GmWorkItem()
            item_s["url"] = url_key
            item_s["source_code"] = response.text
            yield item_s
            good_name = response.css(".mb-8.js-product-title").xpath("./text()").get()
            shop_name = response.css(".Product__Title.js-break-md-right").xpath("./p/a/text()").get()
            shop_url = response.css(".Product__Title.js-break-md-right").xpath("./p/a/@href").get()
            price = response.css(".price.js-meta-price").xpath("./text()").get()
            if price:
                price = re.sub("[^\d\.]","",price)
            product = response.css(".table.table-striped.a11y-text-width").xpath("./tr")
            brand = ""
            category = ""
            size = ""
            fruugo_id = ""
            ean = ""
            retailer_vrn = ""
            colour = ""
            for i in product:
                name_product = i.xpath("./th/text()").get()
                value = i.xpath("./td/text()").get()
                value = value.strip() if value else None
                if not value:
                    value = i.xpath("./td/a/text()").get()
                    value = value.strip() if value else None
                if "Brand" in name_product:
                    brand = value
                if "Category" in name_product:
                    category = value
                if "Size" in name_product:
                    size = value
                if "Fruugo ID" in name_product:
                    fruugo_id = value
                if "EAN" in name_product:
                    ean = value
                if "Retailer VRN" in name_product:
                    retailer_vrn = value
                if "Colour" in name_product:
                    colour = value
            description = response.css(".js-product-description").xpath("./text()").get()
            item = GmWorkItem()
            item["key"] = url_key
            item["good_name"] = good_name
            item["price"] = price
            item["shop_name"] = shop_name
            item["shop_url"] = shop_url
            item["brand"] = brand
            item["category"] = category
            item["size"] = size
            item["goods_id"] = fruugo_id
            item["ean"] = ean
            item["retailer_vrn"] = retailer_vrn
            item["colour"] = colour
            item["description"] = description
            yield item
        else:
            try_result = self.try_again(response,url=url_key)
            yield try_result

    def try_again(self,rsp,**kwargs):
        print("错误了")
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
