# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict


class AllegroSpider(RedisSpider):
    name = 'allegro_sort'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_sort:start_url"

    def start_requests(self):
        url = "https://allegro.pl/mapa-strony/kategorie"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        url = response.request.url
        if response.status == 200:
            item_s = GmWorkItem()
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
                    # sort_url = "https://allegro.pl" + url_totle
                    # yield scrapy.Request(url=sort_url, method="GET", headers=headers, dont_filter=True,
                    #                      meta={"name": name_totle})
                else:
                    print("sort_all有url没有选取", name_totle)
                sort_sun = i.xpath(".//ul/li/a")
                for i in sort_sun:
                    url = i.xpath("./@href").get()
                    name = i.xpath("./text()").get()
                    if url:
                        url = "https://allegro.pl" + url
                        item = GmWorkItem()
                        item["last_name"] = name_totle
                        item["name"] = name
                        item["url"] = url
                        yield item
        else:
            try_result = self.try_again(response,url=response.url)
            yield try_result

    #
    # def parse(self, response):
    #     youxiao = re.search("(gS4GqiXvRSi8oJgNBVklGA)",response.text)
    #     url = response.url
    #     if youxiao:
    #         item_s = GmWorkItem()
    #         last_name = response.meta.get("name")
    #         item_s["url"] = url
    #         item_s["source_code"] = response.text
    #         yield item_s
    #         shop_list = response.xpath("//div[@data-box-id='gS4GqiXvRSi8oJgNBVklGA==']/div/ul//a")
    #         if not shop_list:
    #             print("shop_list有url没有选取",last_name)
    #         for i in shop_list:
    #             url = i.xpath("./@href").get()
    #             name = i.xpath("./text()").get()
    #             url = "https://allegro.pl"+url
    #             item = GmWorkItem()
    #             item["last_name"] = last_name
    #             item["name"] = name
    #             item["url"] = url
    #             yield item
    #
    #     else:
    #         try_result = self.try_again(response,url=url)
    #         yield try_result

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
