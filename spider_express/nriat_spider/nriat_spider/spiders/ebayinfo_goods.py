# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import EbayItemGood
from tools.tools_request.spider_class import RedisSpiderTryagain
from fake_useragent import UserAgent
class EbayinfoShopSpider(RedisSpiderTryagain):
    name = 'ebayinfo_goods'
    allowed_domains = ['ebay.com']
    redis_key = 'ebayinfo_goods:start_url'
    error_key = "ebayinfo_goods:error_url"

    cookie = 'cid=RCRrg6ggTjfzi2Zb%23173818139; __gads=ID=863ff801b7cd819c:T=1597800293:S=ALNI_MZkzf3_NC0nzSYA8qZx_w2TVuD2BQ; s=CgAD4ACBfm4YiMDQ1MDRkMmUxNzQwYTY5YzYxODQwY2U1ZmZmZmVhMDYva9MH; ak_bmsc=B2EC6191699FF383FD58FA462E73527C7D38DA25083B0000A3349A5FD6C22B45~plMt7F3av1uw9hkLWv9bkVrUc3jbgYEC4RI+Vn7OSYlWaCkgvPDS8EqjMxhMsywRfu+q32ULVnkyzxKnYYGsdRZBRPVSk1OQvPIPovs2cfkMKkmZT9u25PzhqkYV95nwiRwZZ4egl9h9MAC69u5BkxorLIgJEz41zzZG6aGN5K+4gFAOENIWtFZprOPVVMaMu9A62rOy/kkGeYVFQxj1+6D4L6QL0MKH47Yyk6bTPV+Bg=; dp1=bu1p/QEBfX0BAX19AQA**635c9ba7^pbf/%232000000e000e00000810002000004617b6827^bl/CN635c9ba7^; nonsession=BAQAAAXQoEGjGAAaAADMABmF7aCczMTAwMDAAygAgY1ybpzA0NTA0ZDJlMTc0MGE2OWM2MTg0MGNlNWZmZmZlYTA2AMsAAV+aO68zlPzn0FghfNmvBRLsa67GhtuRZvg*; npii=btguid/04504d2e1740a69c61840ce5ffffea06635c9ba7^cguid/0450844c1740a6e5b6674517f6cf6d5a635c9ba7^; ebay=%5Ejs%3D1%5Esbf%3D%23000000%5E; bm_sv=71B78F0B3679BC2F50AD7D7BF57687D1~c9528g9D1h5F4Uka+EYR/02FAo81CP0I9ZyKOljff6gzHOwsNCHOP+j8bFase48dDY/jFYHUGhlzLcyFWNmckztaGATEQ7Aqlh/8vqaQZUuwCk5OUMsw+OIGjKs3eIJ4XztbvNCObZrDLyPgEUF2eQ=='
    cookie_dict = {i.split('=')[0]: i.split('=')[1] for i in cookie.split(';')}
    location = r'W:\fake\fake_useragent_0.1.11.json'
    ua = UserAgent(path=location)
    # 构造商品列表页url
    def make_requests_from_url(self, url):
        seller = url
        # seller = "health_from_altai"
        goods_list = f'https://www.ebay.com/sch/{seller}/m.html?_nkw&_armrs=1&_from&rt=nc&LH_PrefLoc=6'
        return scrapy.Request(url=goods_list,
                             #cookies=self.cookie_dict,
                             #headers={'User-Agent':self.ua.random},
                             callback=self.parse_list,meta={"first":True,"key":seller})

    # 获取商品url，和下一页url
    def parse_list(self, response):
        youxiao = "rcnt|sm-md"
        if re.search(youxiao,response.text):
            if response.xpath('//ul[@id="ListViewInner"]'):
                goods_urls = response.xpath(
                    '//ul[@id="ListViewInner"]/li/h3/a/@href').getall()
                for url in goods_urls:
                    yield scrapy.Request(url=url,
                                         #cookies=self.cookie_dict,
                                         #headers={'User-Agent':self.ua.random},
                                         callback=self.parse_goodinfo)
                first = response.meta.get("first")
                key = response.meta.get("key")
                goods_num = response.css(".clt").xpath("./span/text()").get("").strip()
                goods_num = goods_num.replace(" ","")
                if first and goods_num:
                    page = int(int(goods_num)/50)+1 if int(goods_num)%50 else int(int(goods_num)/50)
                    page = min(page,100)
                    for i in range(2,page+1):
                        url = "https://www.ebay.com/sch/m.html?_nkw=&_armrs=1&_from=&_ssn={}&LH_PrefLoc=6&_pgn={}&_skc={}&rt=nc".format(key,i,i*50-50)
                        yield scrapy.Request(url=url,
                                            #headers={'User-Agent':self.ua.random},
                                             #cookies=self.cookie_dict,
                                             callback=self.parse_list,meta={"key":key})
        else:
            yield self.try_again(response)

    def re_data(self, re_guizhe, response):
        data = re.search(re_guizhe, response)
        if data:
            data_data = data.group(1)
            r_data = data_data.strip().replace(',', '')
        else:
            r_data = ''
        return r_data

    # 获取商品详情
    def parse_goodinfo(self, response):
        youxiao = "CenterPanel|error-header"
        if re.search(youxiao,response.text):
            good_id = re.search(r'itm+/(\d+)', response.url)
            if good_id != None:
                good_id = good_id.group(1)
            else:
                good_id = ''
            # source_code = response.text
            good_name = response.xpath('//h1[@class="x-item-title__mainTitle"]/span/text()').get()
            if good_name:
                good_name = good_name.strip().replace(',', '，')
            else:
                good_name = ''

            price_dollar = self.re_data(r'convertedFromValue":(.*?),"', response.text)
            # if price_dollar:
            #     price_dollar = price_dollar.strip().replace(',', '')
            # else:
            #     price_dollar = ''

            price_RMB = self.re_data(r'{"value":(.*?),"convertedFromValue', response.text)
            # if price_RMB != None:
            #     price_RMB = price_RMB.split()[1].strip().replace(',', '')
            # else:
            #     price_RMB = ''

            project_location = self.re_data(r'"所在地：(.*?)","styles', response.text)
            # if project_location:
            #     project_location = project_location.strip().replace(',', '，')
            # else:
            #     project_location = ''

            brand = response.xpath('//span[@itemprop="name"]/text()').getall()
            if brand != []:
                brand = brand[-1].strip().replace(',', '，')
            else:
                brand = ''

            seller_name = self.re_data(r'"username":"(.*?)"}', response.text)
            # if seller_name:
            #     seller_name = seller_name.strip().replace(',', '，')
            # else:
            #     seller_name = ''

            sales_count = response.xpath(
                '//a[@class="vi-txt-underline"]/text()').get()
            if sales_count != None:
                sales_count = sales_count.split()[0]
            else:
                sales_count = ''

            cats_list = self.re_data(r'"breadcrumbsList":(.*?),"meta"', response.text)
            cats = re.findall(r'"text":"(.*?)"}]', cats_list)
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
            # item_s = EbayItemGood(good_id=good_id,  source_code=source_code)
            # yield item_s
        else:
            self.try_again(response)
