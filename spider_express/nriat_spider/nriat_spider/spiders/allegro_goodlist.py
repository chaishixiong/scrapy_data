# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import AllegroItem
from tools.tools_request.spider_class import RedisSpiderTryagain
import re


class AllegroSpiderSpider(RedisSpiderTryagain):
    name = 'allegro_spider'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_spider:start_url"
    error_key = "allegro_spider:error_url"
    custom_settings = {"CONCURRENT_REQUESTS":1,"CHANGE_IP_NUM":50,"DOWNLOADER_MIDDLEWARES":{
    'nriat_spider.middlewares.IpChangeDownloaderMiddleware': 20,
    'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,
    'nriat_spider.middlewares.UserAgentChangeDownloaderMiddleware': 22,
}}
    headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    }

    def start_requests(self):
        url = 'https://allegro.pl/mapa-strony/kategorie'
        yield scrapy.Request(url=url,headers=self.headers,callback=self.get_page,dont_filter=True)

    def get_page(self,response):
        youxiao = "Elektronika"
        if youxiao in response.text:
            caturls = response.xpath('//div[@class = "_2508c_CaabZ _2508c_2fm2a js-navigation-links"]/ul/li/a/@href').getall()
            for i in caturls:
                caturl = 'https://allegro.pl' + i
                for page in range(1,101):
                    url = caturl + '?bmatch=baseline-product-cl-eyesa2-engag-dict45-ele-1-5-1106&p={}'.format(page)
                    yield scrapy.Request(url=url,callback=self.parse,headers=self.headers,meta={'url':url})
        else:
            yield self.try_again(response)

    def parse(self, response):
        youxiao = "__listing_StoreState"
        url = response.meta['url']
        if youxiao in response.text:
            data_str = re.findall('"listingType":"base","__listing_StoreState":"(.*?)","__listing_CookieMonster"', response.text)[0] if re.findall('"listingType":"base","__listing_StoreState":"(.*?)","__listing_CookieMonster"', response.text) else re.findall('"listingType":"gallery","__listing_StoreState":"(.*?)","__listing_CookieMonster"', response.text)[0]
            data_str = data_str.replace('\\\\', '\\')
            data_str = data_str.replace('\\"', '"')
            data_str = data_str.replace('\\u002F', '/')
            data = json.loads(data_str)
            items = data.get("items")
            elements = items.get("elements", {})

            source_code = elements
            item2 = AllegroItem(source_code=source_code)
            yield item2

            if elements != None or elements !=[]:
                for j in elements:
                    try:
                        good_id = j.get("id")
                    except:
                        good_id =''
                    try:
                        good_url = j.get("url", "")
                        good_url = good_url.replace(r"\u002F", "/")
                    except:
                        good_url = ''
                    try:
                        location = j.get("location", {})
                        city = location.get("city")
                    except:
                        city = ''
                    try:
                        title = j.get("title", {})
                        good_name = title.get("text")
                    except:
                        good_name = ''
                    try:
                        status = j.get("type")
                    except:
                        status = ''
                    try:
                        price_list = j.get("price", {})
                        normal = price_list.get('normal')
                        price = normal.get("amount")
                    except:
                        price = ''

                    try:
                        sales = j.get("popularityLabel")
                    except:
                        sales = ''
                    try:
                        seller = j.get("seller", {})
                        shop_id = seller.get("id")
                        shop_super = seller.get("superSeller")
                        shop_name = seller.get("login")
                    except:
                        shop_id = ''
                        shop_super = ''
                        shop_name = ''
                    try:
                        sort_id = j.get("categoryPath")
                    except:
                        sort_id = ''
                    item = AllegroItem(url=url,good_id=good_id,good_url=good_url,city=city,good_name=good_name,status=status,price=price,sales=sales,
                                       shop_id=shop_id,shop_super=shop_super,shop_name=shop_name,sort_id=sort_id)
                    yield item
        else:
            yield self.try_again(response)