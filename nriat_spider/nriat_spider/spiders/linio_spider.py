# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy_redis.spiders import RedisSpider
from tqdm import tqdm
from ..items import LinioItem

class LinioSpiderSpider(RedisSpider):
    name = 'linio_spider'
    allowed_domains = ['www.linio.com.mx']
    # start_urls = ['http://www.linio.com.mx/']
    redis_key = 'linio'

    host = 'http://www.linio.com.mx'
    custom_settings = {
       'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
       'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
       'REDIS_URL': 'redis://192.168.0.230:5208/2',
       'SCHEDULER_PERSIST': True,"CHANGE_IP_NUM":2000,"CONCURRENT_REQUESTS":8
    }
    def start_requests(self):
        with open(r'F:\Pycharm\scrapy测试\GC\data\linio\{cat_url}[cat_url].txt', 'r', encoding='utf-8') as f:
            for i in tqdm(f):
                i = i.replace('\n', '')
                for num in range(1, 18):
                    url = i + str(num)
                    # url = 'https://www.linio.com.mx/s/shoppitronic'
                    # url = 'https://www.linio.com.mx/c/computacion/punto-de-venta?page=1'
                    yield scrapy.Request(url=url, callback=self.parse_shop_list)

    def parse_good_url(self, response):
        urls = response.xpath('//div[@id="catalogue-product-container"]/div/a/@href').getall()
        if urls != []:
            for url in urls:
                real_url = self.host + url

                yield scrapy.Request(url=real_url, callback=self.parse_shop_url)

    def parse_shop_url(self, response):
        url = response.xpath('//a[@class="link-low-md"]/@href').get()
        if url:
            for i in range(1, 18):
                real_url = self.host + url + '?page=' + str(i)
                # real_url = self.host + url + '?page=1'
                yield scrapy.Request(url=real_url, callback=self.parse_shop_list)

    def parse_shop_list(self, response):
        urls = response.xpath('//div[@id="catalogue-product-container"]/div/a/@href').getall()
        shop_name = response.xpath('//h1[@class="section-title"]/text()').get()
        if urls != []:
            for url in urls:
                real_url = self.host + url
                yield scrapy.Request(url=real_url, callback=self.parse_good_info, meta={'shop_name':shop_name})

    def parse_good_info(self, response):

        shop_name = response.meta['shop_name']
        source_code = response.text
        try:
            sku = re.findall(r'oid=(.+?)&', response.url)[0]
        except:
            sku = ''

        try:
            good_name = response.xpath('//span[@class="product-name"]/text()').get()
            good_name = good_name.replace('，', ',')
        except:
            good_name = ''

        try:
            brand = response.xpath('//a[@itemprop="brand"]/text()').get()
        except:
            brand = ''

        try:
            score = response.xpath('//span[@class="star-rating"]/span[1]/text()').get()
        except:
            score = ''

        try:
            price = response.xpath('//div[@class="product-price-lg"]/div[@class="lowest-price"]/span/text()').get()
            price = price.strip().replace('$', '').replace(',', '')
        except:
            price = ''

        try:
            comment = re.findall(r'<span data-anchor="panel-reviews-anchor".+?>(.+?) reseña', response.text)[0]
        except:
            comment = ''

        try:
            cat1 = response.xpath('//ol/li[1]/a/span/text()').get()
        except:
            cat1 = ''

        try:
            cat2 = response.xpath('//ol/li[2]/a/span/text()').get()
        except:
            cat2 = ''

        try:
            cat3 = response.xpath('//ol/li[3]/a/span/text()').get()
        except:
            cat3 = ''

        try:
            cat4 = response.xpath('//ol/li[4]/a/span/text()').get()
        except:
            cat4 = ''

        try:
            cat5 = response.xpath('//ol/li[5]/a/span/text()').get()
        except:
            cat5 = ''

        try:
            cat6 = response.xpath('//ol/li[6]/a/span/text()').get()
        except:
            cat6 = ''
        item1 = LinioItem(shop_name=shop_name, sku=sku, good_name=good_name, brand=brand, score=score, price=price, comment=comment, cat1=cat1, cat2=cat2, cat3=cat3, cat4=cat4, cat5=cat5, cat6=cat6)
        yield item1

        item2 = LinioItem(source_code=source_code)
        yield item2
