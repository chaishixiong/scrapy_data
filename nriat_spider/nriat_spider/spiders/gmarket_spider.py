# -*- coding: utf-8 -*-
import scrapy
from nriat_spider.items import GmarketItem
from tools.tools_request.spider_class import RedisSpiderTryagain
from tools.tools_request.header_tool import headers_todict


class GmarketSpiderSpider(RedisSpiderTryagain):
    name = 'gmarket_spider'
    allowed_domains = ['gmarket.co.kr']
    # start_urls = ['http://gmarket.co.kr/']
    redis_key = 'gmarket_spider:start_url'
    error_key = "gmarket_spider:error_url"

    headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Host: browse.gmarket.co.kr
Pragma: no-cache
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'''


    def make_requests_from_url(self, seed):
        i = seed.strip()
        return scrapy.Request(url=i, headers=headers_todict(self.headers),callback=self.parse_goodinfo)

    def parse_goodinfo(self, response):
        if "box__information" in response.text:
            divs = response.xpath('//div[@class="box__information"]')
            source_code = response.text
            item1 = GmarketItem(source_code=source_code)
            yield item1

            for div in divs:
                shop_id = div.xpath('.//a[@class="link__shop"]/@data-montelena-sell_cust_no').get()
                if shop_id:
                    shop_id = str(shop_id)
                else:
                    shop_id = ''

                good_id = div.xpath('.//a[@class="link__item"]/@data-montelena-goodscode').get()
                if good_id:
                    good_id = str(good_id)
                else:
                    good_id = ''

                good_name = div.xpath('.//span[@class="text__item"]/@title').get()
                if good_name:
                    good_name = good_name.strip().replace('，', '')
                else:
                    good_name = ''

                good_url = div.xpath('.//a[@class="link__item"]/@href').get()
                if good_url:
                    good_url = good_url
                else:
                    good_url = ''

                price = div.xpath('.//strong/text()').get()
                if price:
                    price = price.replace(',', '')
                else:
                    price = ''

                shopping_fee = div.xpath('.//span[@class="text__tag"]/text()').get()
                try:
                    shopping_fee = shopping_fee.split('원')[0].split()[1].replace(',', '')
                except:
                    shopping_fee = ''

                comment = div.xpath('.//li[contains(@class, "feedback-count")]/span[2]/text()').getall()

                try:
                    comment = comment[1].replace(',', '')
                except:
                    comment = ''

                sales_count = div.xpath('.//li[contains(@class, "pay-count")]/span[1]/text()').getall()
                try:
                    sales_count = sales_count[1].replace(',', '')
                except:
                    sales_count = ''

                item2 = GmarketItem(shop_id=shop_id,good_id=good_id,good_name=good_name, good_url=good_url, price=price,
                                    shopping_fee=shopping_fee, comment=comment, sales_count=sales_count)
                yield item2

                shop_url = div.xpath('.//a[@class="link__shop"]/@href').get()
                if shop_url:
                    yield scrapy.Request(url=shop_url,headers=headers_todict(self.headers), callback=self.parse_shopinfo, meta={'shop_id':shop_id, 'shop_url':shop_url})
            next_page = response.xpath('//a[@class="link__page-next"]/@href').get()
            if next_page:
                next_page = 'http://browse.gmarket.co.kr' + next_page
                yield scrapy.Request(url=next_page,headers=headers_todict(self.headers), callback=self.parse_goodinfo)
        else:
            yield self.try_again(response)

    def parse_shopinfo(self, response):
        shop_id = response.meta['shop_id']
        shop_url = response.meta['shop_url']
        if "seller_info_box" in response.text:
            data = response.xpath('//div[@class="seller_info_box"]/dl/dd/text()').getall()
            try:
                shop_name = data[0].replace(',', '，')
            except:
                shop_name = ''
            try:
                boss = data[1].replace(',', '，')
            except:
                boss = ''
            try:
                tel = data[2].replace(',', '，')
            except:
                tel = ''
            try:
                fax = data[4].replace(',', '，')
            except:
                fax = ''
            try:
                license_num = data[5].replace(',', '，')
            except:
                license_num = ''
            try:
                email = response.xpath('//div[@class="seller_info_box"]//dd/a/text()').get()
            except:
                email = ''
            try:
                address = data[6].replace(',', '，')
            except:
                address = ''
            pipeline_level = 'shopinfo'
            item3 = GmarketItem(shop_id=shop_id, shop_name=shop_name, shop_url=shop_url, boss=boss, tel=tel, fax=fax,
                                license_num=license_num, email=email, address=address, pipeline_level=pipeline_level)
            yield item3
        else:
            yield self.try_again(response)