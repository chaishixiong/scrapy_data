# -*- coding: utf-8 -*-
import scrapy
from tqdm import tqdm
import json
from ..items import KilimallItem
from scrapy_redis.spiders import RedisSpider

class KilimallSpiderSpider(RedisSpider):
    name = 'kilimall_spider'
    allowed_domains = []
    #start_urls = ['http://kilimall.ng/new/']
    redis_key = 'kilimall:start_urls'
    headers = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',}

    custom_settings = {
		'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
		'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
		'REDIS_URL': 'redis://192.168.0.230:5208/3',
		'SCHEDULER_PERSIST': True,
		"CHANGE_IP_NUM": 1000, "CONCURRENT_REQUESTS": 8
	}

    def start_requests(self):
        with open(r'D:\Spider\kilimall\shop_id.txt', 'r',encoding='utf_8') as f:
            for i in tqdm(f):
                i = i.replace('\n', '')
                page = 1
                url = 'https://api.kilimall.com/ng/v1/product/search?size=40&page={}&gc_id={}'.format(page,i)
                print(url)
                yield scrapy.Request(url=url,callback=self.parse,headers=self.headers,meta={'i':i})

    def parse(self, response):
        host = 'https://api.kilimall.com/ng/v1/product/search?size=40&page={}&gc_id={}'
        # meta：传 i 数据
        id = response.meta.get("i")
        # print(host)
        res = response.text
        try:
            obj = json.loads(res)
        except Exception as e:
            obj={}


        item1 = KilimallItem(source_code = response.text)
        # yield item1

        item2 = obj.get('data',{}).get('products')
        if item2 != None or item2 != []:
            for i in item2:

                # 商品id
                goods_id = i.get("goods_id","")
                # print(goods_id)

                # 商品名
                good_name = i.get("name","")
                # print(good_name)

                # 现价
                new_price = i.get("price","")
                # print(new_price)

                # 原价
                old_price = i.get("marketprice","")
                # print(old_price)

                #店名
                shop_name = i.get("store_name","")
                # print(shop_name)

                #  店铺评分
                score = i.get("rate","")
                # print(score)

                # # 评论数
                comment_nums = i['ratings']
                # print(comment_nums)

                item1 = KilimallItem(goods_id=goods_id, good_name=good_name,
                                     new_price=new_price,old_price=old_price,
                                     shop_name=shop_name, score=score,comment_nums=comment_nums)
                yield item1
            maxpage = obj.get("meta", {}).get("last_page", "")
            page = obj.get("meta",{}).get("current_page","")
            print(page, maxpage)
            print(type(maxpage))
            # 翻页
            if page < maxpage:
                next_url = host.format(page + 1, id)
                yield scrapy.Request(url=next_url, callback=self.parse, headers=self.headers, meta={ 'page': page + 1, 'i': id})
