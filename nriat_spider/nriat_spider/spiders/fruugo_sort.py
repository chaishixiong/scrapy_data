# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
import json
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class FruugoSpider(RedisSpider):
    name = 'fruugo_sort'
    allowed_domains = ['fruugo.co.uk/']
    start_urls = ['https://www.fruugo.co.uk/']
    redis_key = "fruugo_sort:start_url"
    error_key = "fruugo_sort:error_url"

    custom_settings = {"CONCURRENT_REQUESTS":4,}

    def start_requests(self):
        headers = self.get_headers(1)
        yield scrapy.Request(url="https://www.fruugo.co.uk/marketplace/api/site-navigation/header?language=en",headers=headers,callback=self.sort_all)

    def sort_all(self,response):
        request_url = response.request.url
        if response.status == 200:
            headers = self.get_headers(1)
            data_json = json.loads(response.text)
            items = data_json.get("items")
            for i in items:
                id = i.get("id")
                link = i.get("link")
                url = link.get("href")
                name = link.get("text")
                second_item = i.get("items")
                if second_item:
                    for j in second_item:
                        id_second = j.get("id")
                        link_s = j.get("link")
                        url_s = link_s.get("href")
                        name_s = link_s.get("text")
                        third_s = j.get("items")
                        if third_s:
                            for z in third_s:
                                id_third = z.get("id")
                                link_t = z.get("link")
                                url_t = link_t.get("href")
                                name_t = link_t.get("text")
                                if url_t:
                                    url_t = "https://www.fruugo.co.uk" + url_t
                                    meta = {"id":id_third,"category":[name,name_s,name_t],"first_page":True}
                                    yield scrapy.Request(url=url_t, method="GET", headers=headers, dont_filter=True,
                                                         meta=meta)
                        else:
                            print("第2级缺少：",id_second)
                else:
                    print("第1级缺少：",id)
        else:
            try_result = self.try_again(response,url=request_url)
            yield try_result


    def parse(self, response):
        youxiao = re.search("(information-holder|results)", response.text)
        url_key = response.request.url
        id = response.meta.get("id")
        category = response.meta.get("category")
        first_page = response.meta.get("first_page")
        page_num = response.meta.get("page_num",1)
        if youxiao:
            item_s = GmWorkItem()
            item_s["url"] = url_key
            item_s["source_code"] = response.text
            yield item_s
            goods_num = response.css(".results").xpath("./text()").get()#总商品数
            if goods_num:
                match = re.search("of ([^ ]+) results", goods_num)
                if match:
                    goods_num = match.group(1)
                    goods_num = goods_num.replace(",", "")
            shop_list = response.css(".row.information-holder").xpath("./a")
            if not shop_list:
                print("shop_list有url没有选取",id)
            for i in shop_list:
                url = i.xpath("./@href").get()
                name = i.xpath("./span/text()").get()
                price = i.xpath("./strong/text()").get()
                url = "https://www.fruugo.co.uk" + url

                item = GmWorkItem()
                item["key"] = url_key
                item["name"] = name
                item["url"] = url
                item["price"] = price
                item["goods_num"] = goods_num
                item["category"] = category
                yield item
            if first_page and goods_num:
                headers = self.get_headers(1)
                limitnum = 1000
                per_page = 64
                num = self.get_pagenum(int(goods_num), per_page)
                if num > limitnum:
                    num = limitnum
                for i in range(2, num + 1):
                    next_url = url_key + "?page={}".format(i)
                    meta = {"id": id, "category": category,"page_num" : page_num}
                    yield scrapy.Request(url=next_url, method="GET", headers=headers, dont_filter=True,meta=meta)
        else:
            try_result = self.try_again(response,url=url_key)
            yield try_result

    def get_pagenum(self,num, page):
        if num % page:
            goods_num = int(num / page) + 1
        else:
            goods_num = int(num / page)
        return goods_num

    def try_again(self,rsp,**kwargs):
        max_num = 20
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
