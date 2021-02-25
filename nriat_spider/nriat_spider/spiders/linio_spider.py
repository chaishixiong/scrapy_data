# -*- coding: utf-8 -*-
import scrapy
from tools.tools_request.spider_class import RedisSpiderTryagain
from ..items import LinioItem
import re

class LinioSpiderSpider(RedisSpiderTryagain):
    name = 'linio_spider'
    allowed_domains = ['www.linio.com.mx']
    # start_urls = ['http://www.linio.com.mx/']
    redis_key = 'linio:start_url'
    error_key = "linio:error_url"
    host = 'https://www.linio.com.mx'
    custom_settings = {
        "CHANGE_IP_NUM":2000,
        "CONCURRENT_REQUESTS":2,
        "DEFAULT_REQUEST_HEADERS" : {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    }

    def start_requests(self):
        url = "https://www.linio.com.mx/"
        yield scrapy.Request(url=url,callback=self.get_page,dont_filter=True)

    def get_page(self,response):
        yuoxiao = "main-menu"
        if yuoxiao in response.text:
            cat1 = response.xpath('//div[@id="main-menu"]//ul/li/a/@href').getall()
            for i in cat1:
                if i != 'https://viajes.linio.com.mx/paquetes'and i != '/cm/solo-hoy-ofertas':
                    real_cat1 = 'https://www.linio.com.mx' + i
                    yield scrapy.Request(url=real_cat1, callback=self.get_page1)
        else:
            yield self.try_again(response)

    def get_page1(self,response):
        youxiao = "navbar-title"
        has_cat3 = response.meta.get("has_cat3")
        if youxiao in response.text:
            cat2 = response.xpath('//div[@class="catalogue-list"]/ul/li/a/@href').getall()
            for n in cat2:
                real_cat2 = 'https://www.linio.com.mx' + n + '?page='
                for num in range(1, 18):
                    url = real_cat2 + str(num)
                    yield scrapy.Request(url=url,callback=self.parse_shop_list)
            cat3 = response.xpath('//div[@class="banner-layout-5"]/div/a/@href').getall()
            if cat3 and not has_cat3:
                for m in cat3:
                    cat3_url = 'https://www.linio.com.mx' + m
                    yield scrapy.Request(url=cat3_url,callback=self.get_page1)
        else:
            yield self.try_again(response)


    def parse_shop_list(self, response):
        match = re.search("catalogue-product-container|no encontró",response.text)
        if match:
            urls = response.xpath('//div[@id="catalogue-product-container"]/div/a/@href').getall()
            # shop_name = response.xpath('//h1[@class="section-title"]/text()').get()
            if urls != []:
                for url in urls:
                    real_url = self.host + url
                    yield scrapy.Request(url=real_url, callback=self.parse_good_info,)
        else:
            try_result = self.try_again(response)
            yield try_result


    def parse_good_info(self, response):
        match = re.search("product-name",response.text)
        if match:
            # shop_name = response.meta['shop_name']
            # print(shop_name)
            source_code = response.text
            # 商品id
            try:
                good_id = re.findall(r'oid=(.+?)&', response.url)[0]
            except:
                good_id = ''
            # print(good_id)
            # 商品名称
            try:
                good_name = response.xpath('//span[@class="product-name"]/text()').get()
                good_name = good_name.replace('，', ',')
            except:
                good_name = ''
            # print(good_name)
            # 分类
            try:
                brand = response.xpath('//a[@itemprop="brand"]/text()').get()
            except:
                brand = ''
            # print(brand)
            # 商品评分
            try:
                good_score = response.xpath('//span[@class="star-rating"]/span[1]/text()').get()
            except:
                good_score = ''
            # print(good_score)
            # 商品价格
            try:
                price = response.xpath('//div[@class="product-price-lg"]/div[@class="lowest-price"]/span/text()').get()
                price = price.strip().replace('$', '').replace(',', '')
            except:
                price = ''
            # print(price)
            # 商品评论
            try:
                comment = re.findall(r'<span data-anchor="panel-reviews-anchor".+?>(.+?) reseña', response.text)[0]
            except:
                comment = ''
            # print(comment)

            try:
                cat1 = response.xpath('//ol/li[1]/a/span/text()').get()
            except:
                cat1 = ''
            # print(cat1)

            try:
                cat2 = response.xpath('//ol/li[2]/a/span/text()').get()
            except:
                cat2 = ''
            # print(cat2)

            try:
                cat3 = response.xpath('//ol/li[3]/a/span/text()').get()
            except:
                cat3 = ''
            # print(cat3)

            try:
                cat4 = response.xpath('//ol/li[4]/a/span/text()').get()
            except:
                cat4 = ''
            # print(cat4)

            # 店铺名称
            try:
                shop_name = response.xpath('//a[@class="link-low-md"]//text()').get()
            except:
                shop_name = ''
            # print(shop_name)

            # 店铺评分
            try:
                shop_score = response.xpath('//span[@class="score"]/text()').get()
            except:
                shop_score = ''
            # print(shop_score)

            # 店铺url
            try:
                shop_url = response.xpath('//div[@class = "seller-name-rating-section"]/a/@href').get()
                shop_url = 'https://www.linio.com.mx' + str(shop_url)
            except:
                shop_url = ''
            # print(shop_url)
            # print('=================================================================================================')

            item1 = LinioItem(shop_name=shop_name, good_id=good_id, good_name=good_name,
                              brand=brand, good_score=good_score, price=price, comment=comment,
                              cat1=cat1, cat2=cat2, cat3=cat3, cat4=cat4)
            yield item1

            item2 = LinioItem(source_code=source_code)
            yield item2

            item3 = LinioItem(good_id=good_id, shop_name=shop_name, shop_url=shop_url, shop_score=shop_score, cat3=cat3,
                              pipeline_level='shopinfo')
            yield item3
        else:
            yield self.try_again(response)