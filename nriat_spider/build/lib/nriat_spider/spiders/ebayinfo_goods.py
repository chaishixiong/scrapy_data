# -*- coding: utf-8 -*-
import re

import scrapy
from tqdm import tqdm
# from scrapy_redis_cluster.spiders import RedisSpider
from nriat_spider.items import EbayItemGood
from scrapy_redis.spiders import RedisSpider

class EbayinfoShopSpider(RedisSpider):
    name = 'ebayinfo_goods'
    allowed_domains = ['ebay.com']
    redis_key = 'ebayinfo_goods:start_urls'

    # 使用单独的redis配置
    custom_settings = {
       'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
       'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
       'REDIS_URL': 'redis://192.168.0.230:5208/2',
       'SCHEDULER_PERSIST': True,
        "CHANGE_IP_NUM": 5000, "CONCURRENT_REQUESTS": 8
    }

    cookie = 'cid=VgcN7ONlyOrjxfsC%231813606462; ak_bmsc=62615874530979DBAF318158237098EB17CEEEB4775A0000F2E6175E92D5F56B~plfmo9iX5RI0N/5pupPjnikpkfGca/k7FDUwv8Q3KAToE7/R++7+DawR2VIy1x//Z87n9V5tcV2htfTEUTQFaljz4HxQ+l7sgBNN3amVgxHR1FJusX9zKPCgZVtPzAtoE8HvJkxtwHD3RPuR5gzCHN+cIHZ5ucWwgo78OgQxGDMSyrbhkEBsPbdVamDhWZoVFpfRtaZ2S/IHtNnLFVarYrJ8zbE0wgb/TCgLYMG+YGb4c=; JSESSIONID=FC05E537984BD2ACDA886B715FB2AEF2; cssg=16c02ef516f0a990b1aefec1fd316344; npii=btguid/16c02ef516f0a990b1aefec1fd31634461da541a^cguid/16c05b0a16f0aaaa63560440ff22eb1261da541a^; bm_sv=E346EE51929F9670222FFE71B6D97B20~XhtZSfJNMJps9uhVfY3fUG6rd0XRoQE2cUlmnWIlQom3NrSf8ON4sfgS+JTqDfzGT9AOn3+Gqtrd4XwWw6ty561Zk4s5FdB/bhEtHcNK/qO7toN/0NU3ncTH0iS1h/jg5ugYSpABRL7e3LgSBGCxaw==; ns1=BAQAAAW+HmcDdAAaAANgATF/5IJtjNzJ8NjAxXjE1NzY2NDc3ODQyNjleXjFeM3wyfDV8NHw3fDExXjFeMl40XjNeMTJeMTJeMl4xXjFeMF4xXjBeMV42NDQyNDU5MDc16+xmu7Adm+IGG7V1s8hXYSIk+a0*; dp1=btzo/-1e05e17fb2b^u1p/QEBfX0BAX19AQA**61da541b^bl/CNen-US61da541b^pbf/%23e000e000008100020000005ff9209b^; s=CgAD4ACBeGT6bMTZjMDJlZjUxNmYwYTk5MGIxYWVmZWMxZmQzMTYzNDQA7gBoXhk+mzMGaHR0cHM6Ly93d3cuZWJheS5jb20vc2NoL3dhcmdhbWUtdmV0ZXJhbi9tLmh0bWw/X25rdyZfYXJtcnM9MSZfZnJvbSZydD1uYyZMSF9QcmVmTG9jPTYjaXRlbTNiM2ZlOWI1NzMHEpbjjA**; nonsession=BAQAAAW+HmcDdAAaAAAgAHF4/ehsxNTc4NjI2MTA4eDI1NDQ3NTM1MTQxMXgweDJZADMABl/5IJszMTAwMDAAywACXhf0IzI3AMoAIGHaVBsxNmMwMmVmNTE2ZjBhOTkwYjFhZWZlYzFmZDMxNjM0NLFXjx9BcLQlfLMKuIHR2uDFpquF; ebay=%5Esbf%3D%23400000000010000100000%5Ejs%3D1%5E'

    cookie_dict = {i.split('=')[0]: i.split('=')[1] for i in cookie.split(';')}

    # 构造商品列表页url
    def parse(self, response):
        with open(r'W:/GC/ebay/{2_2_ebay_店铺名称}[卖家名称].txt', 'r', encoding='utf-8') as f:
            sellers_name = f.readlines()
            for seller_name in tqdm(sellers_name):
                seller = seller_name.strip()

                goods_list = f'https://www.ebay.com/sch/{seller}/m.html?_nkw&_armrs=1&_from&rt=nc&LH_PrefLoc=6'
                yield scrapy.Request(url=goods_list,
                                     cookies=self.cookie_dict,
                                     callback=self.parse_list)

    # 获取商品url，和下一页url
    def parse_list(self, response):

        if response.xpath('//ul[@id="ListViewInner"]'):

            # # 保存列表页源码
            # with open(r'D:/Spider_Demo/goods_list_html/' + seller_name + str(self.count) + '.html', 'w', encoding='utf-8') as f:
            #     f.write(response.text)

            goods_urls = response.xpath(
                '//ul[@id="ListViewInner"]/li/h3/a/@href').getall()

            for url in goods_urls:
                yield scrapy.Request(url=url,
                                     cookies=self.cookie_dict,
                                     callback=self.parse_goodinfo)

            if response.xpath('//td[@class="pagn-next"]'):
                next_page = response.xpath(
                    '//td[@class="pagn-next"]/a/@href').get()
                if next_page != 'javascript:;':
                    yield scrapy.Request(url=next_page,
                                         cookies=self.cookie_dict,
                                         callback=self.parse_list)

    # 获取商品详情
    def parse_goodinfo(self, response):

        good_id = re.search(r'itm.+/(\d+)', response.url)

        if good_id != None:
            good_id = good_id.group(1)
        else:
            good_id = ''

        ll = response.body.decode()
        source_code = ll.replace('\n', '').replace('\t', '')
        good_name = response.xpath('//h1[@id="itemTitle"]/text()').get()
        if good_name:
            good_name = good_name.strip().replace(',', '，')
        else:
            good_name = ''

        price_dollar = response.xpath('//span[@id="prcIsum"]/@content').get()
        if price_dollar:
            price_dollar = price_dollar.strip().replace(',', '')
        else:
            price_dollar = ''

        price_RMB = response.xpath(
            '//div[@id="prcIsumConv"]/span/text()').get()
        if price_RMB != None:
            price_RMB = price_RMB.split()[1].strip().replace(',', '')
        else:
            price_RMB = ''

        project_location = response.xpath(
            '//span[@itemprop="availableAtOrFrom"]/text()').get()
        if project_location:
            project_location = project_location.strip().replace(',', '，')
        else:
            project_location = ''

        brand = response.xpath('//span[@itemprop="name"]/text()').getall()
        if brand != []:
            brand = brand[-1].strip().replace(',', '，')
        else:
            brand = ''

        seller_name = response.xpath(
            '//span[@class="mbg-nw"]/font/font/text()|//span[@class="mbg-nw"]/text()').get()
        if seller_name:
            seller_name = seller_name.strip().replace(',', '，')
        else:
            seller_name = ''

        sales_count = response.xpath(
            '//a[@class="vi-txt-underline"]/text()').get()
        if sales_count != None:
            sales_count = sales_count.split()[0].replace('，', '')
        else:
            sales_count = ''

        cats = response.xpath('//li[@class="bc-w"]//span/text()').getall()

        if len(cats) == 0:
            cat_1 = cat_2 = cat_3 = cat_4 = cat_5 = cat_6 = ' '
        elif len(cats) == 1:
            cat_1 = cats[0].strip().replace(',', '，')
            cat_2 = cat_3 = cat_4 = cat_5 = cat_6 = ''
        elif len(cats) == 2:
            cat_1, cat_2 = cats[0].strip().replace(
                ',', '，'), cats[1].strip().replace(',', '，')
            cat_3 = cat_4 = cat_5 = cat_6 = ''
        elif len(cats) == 3:
            cat_1, cat_2, cat_3 = cats[0].strip().replace(
                ',', '，'), cats[1].strip().replace(',', '，'), cats[2].strip().replace(',', '，')
            cat_4 = cat_5 = cat_6 = ''
        elif len(cats) == 4:
            cat_1, cat_2, cat_3, cat_4 = cats[0].strip().replace(',', '，'), cats[1].strip().replace(
                ',', '，'), cats[2].strip().replace(',', '，'), cats[3].strip().replace(',', '，')
            cat_5 = cat_6 = ''
        elif len(cats) == 5:
            cat_1, cat_2, cat_3, cat_4, cat_5 = cats[0].strip().replace(',', '，'), cats[1].strip().replace(
                ',', '，'), cats[2].strip().replace(',', '，'), cats[3].strip().replace(',', '，'), cats[4].strip().replace(',', '，')
            cat_6 = ''
        else:
            cat_1, cat_2, cat_3, cat_4, cat_5, cat_6, = cats[0].strip().replace(',', '，'), cats[1].strip().replace(',', '，'), cats[2].strip(
            ).replace(',', '，'), cats[3].strip().replace(',', '，'), cats[4].strip().replace(',', '，'), cats[5].strip().replace(',', '，')

        item = EbayItemGood(good_id=good_id, good_name=good_name, price_dollar=price_dollar, price_RMB=price_RMB,
                            project_location=project_location, brand=brand, seller_name=seller_name,
                            sales_count=sales_count, cat_1=cat_1, cat_2=cat_2, cat_3=cat_3, cat_4=cat_4, cat_5=cat_5,
                            cat_6=cat_6)

        yield item
        item_s = EbayItemGood(good_id=good_id,  source_code=source_code)

        yield item_s
