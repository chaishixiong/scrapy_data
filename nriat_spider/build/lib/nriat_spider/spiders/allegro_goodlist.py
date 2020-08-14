# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import json
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class AllegroSpider(RedisSpider):
    name = 'allegro_goodlist'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_goodlist:start_url"
    # file_name = r"W:\scrapy_web\allegro_sort-data_合并.txt[F3].txt"
    error_key = "allegro_goodlist:error_url"
    custom_settings = {"REDIRECT_ENABLED":True}

    def start_requests(self):
        url = "https://allegro.pl/mapa-strony/kategorie"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        url = response.request.url
        if response.status == 200:
            item_s = GmWorkItem()
            headers = self.get_headers(1)
            item_s["url"] = url
            item_s["source_code"] = response.text
            yield item_s
            sort = response.xpath("//div[@data-box-id='v2teobNjRByj3C0kzZSwig==']/div/div/div")
            for i in sort:
                sort_totle = i.css(".container-header._1s2v1._n2pii._sdhee")
                name_totle = sort_totle.xpath("./text()").get()
                url_totle = sort_totle.xpath("./small/a/@href").get()
                if url_totle:
                    pass
                else:
                    print("sort_all有url没有选取", name_totle)
                sort_sun = i.xpath(".//ul/li/a")
                for i in sort_sun:
                    url = i.xpath("./@href").get()
                    name = i.xpath("./text()").get()
                    if url:
                        url = "https://allegro.pl" + url
                        yield scrapy.Request(url=url, method="GET", headers=headers, meta={"page_first": True})
                        # item = GmWorkItem()
                        # item["last_name"] = name_totle
                        # item["name"] = name
                        # item["url"] = url
                        # yield item
        else:
            try_result = self.try_again(response,url=response.url)
            yield try_result

    # def seed_requests(self, response):
    #     # url = "https://allegro.pl/kategoria/materialy-opatrunkowe-opatrunki-specjalistyczne-300385"
    #     headers = self.get_headers(1)
    #     with open(self.file_name,"r",encoding="utf-8") as f:
    #         for i in f:
    #             url = i.strip()
    #             yield scrapy.Request(url=url,method="GET",headers=headers,meta={"page_first":True})

    def parse(self,response):
        page_first = response.meta.get("page_first")
        url = response.url
        match = re.search('StoreState_base":"([\s\S]*?)","__listing_CookieMonster_base',response.text)
        if not match:
            match = re.search('StoreState_gallery":"([\s\S]*?)","__listing_CookieMonster_gallery', response.text)
        # if not match:
        #     match = re.search("listing_StoreState_gallery'] ?= ?({.*?});</script>", response.text)#这里没改
        if match:
            item_s = GmWorkItem()
            item_s["url"] = url
            item_s["source_code"] = response.text
            yield item_s
            num = response.css("._1h7wt._1fkm6._g1gnj._3db39_3i0GV._3db39_XEsAE").xpath("./text()").get()
            page_num = ""
            if num:
                page_num = num.replace(" ","")
            data_str = match.group(1)
            data_str = data_str.replace('\\\\','\\')
            data_str = data_str.replace('\\"','"')
            data_str = data_str.replace('\\u002F','/')
            try:
                data = json.loads(data_str)
                items = data.get("items")
                items_groups = items.get("itemsGroups",{})
                for i in items_groups:
                    good_list = i.get("items")
                    for j in good_list:
                        good_id = j.get("id")
                        good_url = j.get("url","")
                        good_url = good_url.replace(r"\u002F","/")
                        location = j.get("location",{})
                        city = location.get("city")
                        title = j.get("title",{})
                        good_name = title.get("text")
                        status = j.get("type")
                        price_json = j.get("price",{})
                        normal = price_json.get("normal",{})
                        price = normal.get("amount")
                        sales = j.get("bidInfo")
                        seller = j.get("seller",{})
                        shop_id = seller.get("id")
                        shop_super = seller.get("superSeller")
                        shop_name = seller.get("login")
                        sort_id = j.get("categoryPath")
                        item = GmWorkItem()
                        item["key"] = url
                        item["page_num"] = page_num
                        item["id"] = good_id
                        item["goods_url"] = good_url
                        item["city"] = city
                        item["good_name"] = good_name
                        item["status"] = status
                        item["price"] = price
                        item["sales_num"] = sales
                        item["shop_id"] = shop_id
                        item["shop_super"] = shop_super
                        item["shop_name"] = shop_name
                        item["sort_id"] = sort_id
                        yield item
            except:
                try_result = self.try_again(response, url=url,type=2)
                yield try_result

            if page_first and page_num:
                headers = self.get_headers(1)
                for i in range(2, int(page_num) + 1):
                    url_next = url + "?p={}".format(i)
                    yield scrapy.Request(url=url_next, method="GET", headers=headers)
        else:
            try_result = self.try_again(response, url=url,type=1)
            yield try_result

    def try_again(self,rsp,**kwargs):
        max_num = 3
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