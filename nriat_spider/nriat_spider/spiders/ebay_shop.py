# -*- coding: utf-8 -*-
#未使用
import scrapy

from scrapy_redis.spiders import RedisSpider


class EbaySpider(RedisSpider):
    name = 'ebay_shop'
    allowed_domains = ['ebay.com']
    redis_key = 'ebay:start_urls'
    # start_urls = 'https://www.ebay.com/n/all-categories'


    # 一级分类
    def parse(self, response):
        category1_urls = response.xpath('//ul[@class="sub-cats"]/li/a/@href').getall()
        for category1_url in category1_urls:
            yield scrapy.Request(url=category1_url,
                                 callback=self.parse_category2)

    # 二级分类
    def parse_category2(self, response):
        category2_urls = []
        if response.xpath('//div[@class="srp-rail__left"]'):
            urls = response.xpath(
                '//div[@class="srp-rail__left"]//li[@class="srp-refine__category__item"]/a/@href').getall()
            for url in urls:
                category2_urls.append(url)
        elif response.xpath('//div[@class="dialog__cell"]'):
            urls = response.xpath('//div[@class="dialog__cell"]/section//li/a/@href').getall()
            for url in urls:
                category2_urls.append(url)
        for category2_url in category2_urls:
            category2_url = category2_url + '?rt=nc&LH_PrefLoc=6'
            yield scrapy.Request(url=category2_url,
                                 callback=self.parse_good)

    # 二级分类下列表页的商品url
    def parse_good(self, response):
        good_urls = []
        if response.xpath('//div[starts-with(@class,"srp-river-results")]'):
            urls = response.xpath('//ul[starts-with(@class,"srp-results")]//a[@class="s-item__link"]/@href').getall()
            for url in urls:
                good_urls.append(url)
        if response.xpath('//section[starts-with(@class,"b-module b-list b-listing")]'):
            urls = response.xpath('//ul[@class="b-list__items_nofooter"]//a[@class="s-item__link"]/@href').getall()
            for url in urls:
                good_urls.append(url)
        for good_url in good_urls:
            yield scrapy.Request(url=good_url,
                                 callback=self.parse_seller)

        # 判断下一页
        if response.xpath('//a[@rel="next"]'):
            next_page = response.xpath('//a[@rel="next"]/@href').get()
            if next_page != '#':
                yield scrapy.Request(url=next_page,
                                     callback=self.parse_good)


    # 获取商家名称
    def parse_seller(self, response):
        seller_name = response.xpath(
            '//span[@class="mbg-nw"]/text()|//span[@class="app-sellerpresence__sellername"]/span/text()|//div[@class="seller-persona "]/span[2]/a[1]/text()').get()
        if seller_name:
            with open('W:/GC/ebay/ebay_解析/ebay_sellerID_解析/{采集_ebay_类目商品获取店铺名称}[卖家名称].txt', 'a', encoding='utf-8') as f:
                f.write(seller_name + '\n')