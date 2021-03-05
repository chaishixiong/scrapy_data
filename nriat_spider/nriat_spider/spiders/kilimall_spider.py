# -*- coding: utf-8 -*-
import scrapy
import re
import json
from ..items import KilimallItem
from tools.tools_request.spider_class import RedisSpiderTryagain

class KilimallSpiderSpider(RedisSpiderTryagain):
    name = 'kilimall_spider'
    allowed_domains = []
    #start_urls = ['http://kilimall.ng/new/']
    redis_key = 'kilimall:start_url'
    error_key = "kilimall:error_url"

    headers = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',}

    custom_settings = {
		"CHANGE_IP_NUM": 100, "CONCURRENT_REQUESTS": 4
	}

    def start_requests(self):
        url = 'https://www.kilimall.co.ke/new/'
        yield scrapy.Request(url=url,headers=self.headers,callback=self.get_page,dont_filter=True)

    def get_page(self,response):
        youxiao = "parent_id"
        if youxiao in response.text:
            gc_id = re.findall('{gc_id:(.*?),parent_id:.*?,gc_name:.*?', response.text)
            for i in gc_id:
                page = 1
                url = 'https://api.kilimall.com/ke/v1/product/search?size=40&page={}&gc_id={}'.format(page, i)
                yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, meta={'i': i})
        else:
            yield self.try_again(response)

    def parse(self, response):
        youxiao = "data"
        if youxiao in response.text:
            host = 'https://api.kilimall.com/ke/v1/product/search?size=40&page={}&gc_id={}'
            id = response.meta.get("i")
            res = response.text
            try:
                obj = json.loads(res)
            except Exception as e:
                obj = {}
            item1 = KilimallItem(source_code=response.text)
            yield item1
            data = obj.get('data', {}).get('products')
            if data != None and data != []:
                for i in data:
                    # 商品id
                    goods_id = i.get("goods_id", "")
                    # print(goods_id)

                    # 商品url
                    good_url = 'https://www.kilimall.co.ke/new/goods/' + str(goods_id)
                    # print(good_url)

                    # 商品名
                    good_name = i.get("name", "")
                    # print(good_name)

                    # 现价
                    new_price = i.get("price", "")
                    # print(new_price)

                    # 原价
                    old_price = i.get("marketprice", "")
                    # print(old_price)

                    # 店铺 id
                    shop_id = i.get('store_id', "")
                    # print(shop_id)

                    # 店名
                    shop_name = i.get("store_name", "")
                    # print(shop_name)

                    #  店铺评分
                    score = i.get("rate", "")
                    # print(score)

                    # # 评论数
                    comment_nums = i['ratings']
                    # print(comment_nums)

                    # 分类
                    category = obj.get('data', {}).get('category', "").get('name', "")
                    # print(category)

                    item2 = KilimallItem(goods_id=goods_id, good_url=good_url, good_name=good_name,
                                         new_price=new_price, old_price=old_price, shop_id=shop_id,
                                         comment_nums=comment_nums, category=category)

                    yield item2
                    shop_url = 'https://www.kilimall.co.ke/new/store/' + str(shop_id)

                    item3 = KilimallItem(shop_url=shop_url, shop_id=shop_id, shop_name=shop_name, score=score,
                                         category=category, pipeline_level='shopinfo')
                    yield item3
                maxpage = obj.get("meta", {}).get("last_page", "")
                page = obj.get("meta", {}).get("current_page", "")

                # 翻页
                if page < maxpage:
                    next_url = host.format(page + 1, id)
                    yield scrapy.Request(url=next_url, callback=self.parse, headers=self.headers,
                                         meta={'page': page + 1, 'i': id})
        else:
            self.try_again(response)

