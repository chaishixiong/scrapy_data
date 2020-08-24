# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import json
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class ShopeeGoodSpider(RedisSpider):
    name = 'shopee_good'
    allowed_domains = ['shopee.com.my']
    start_urls = ['http://shopee.com.my/']
    redis_key = "shopee_good:start_url"
    shop_url = 'https://shopee.com.my/api/v2/shop/get?shopid={}'
    error_key = "shopee_good:error_url"
    custom_settings = {"CHANGE_IP_NUM":50}

    def start_requests(self):
        url = "http://www.baidu.com"
        yield scrapy.Request(url=url, method="GET",callback=self.seed_request)

    def seed_request(self,response):
        headers = self.get_headers(1)
        file_name = r"W:\scrapy_xc\shopee_sort-data_合并.txt[F5].txt"#seed:取上步的第5个
        with open(file_name,"r",encoding="utf-8") as f:
            for i in f:
                data = i.split(",")
                page = 1#最多100页
                match_id = data[0]
                page_num = (page - 1) * 50
                meta = {"match_id":match_id,"page":page}
                url = 'https://shopee.com.my/api/v2/search_items/?by=sales&limit=50&match_id={}&newest={}&order=desc&page_type=search&version=2'.format(match_id,page_num)
                yield scrapy.Request(url=url,headers=headers,meta=meta)

    def parse(self, response):
        youxiao = re.search('("error":null)',response.text)
        meta = response.meta
        match_id = meta.get("match_id")
        page = meta.get("page")
        url = response.request.url
        headers = self.get_headers(1)
        if youxiao:
            item_s = GmWorkItem()
            item_s["key"] = match_id
            item_s["pipeline_level"] = "list"
            item_s["source_code"] = response.text
            yield item_s
            try:
                data = json.loads(response.text)
                if page == 1:
                    total_count = data.get("total_count")
                    if total_count > 5000:
                        total_count = 5000
                    pages = int(total_count/50)*50 if total_count%50==0 else int(total_count/50)*50+50
                    for i in range(50,pages,50):
                        page_num_r = i
                        new_page = int((page_num_r+50)/50)
                        meta_r = {"match_id": match_id, "page": new_page}
                        url_r = 'https://shopee.com.my/api/v2/search_items/?by=sales&limit=50&match_id={}&newest={}&order=desc&page_type=search&version=2'.format(
                            match_id, page_num_r)
                        yield scrapy.Request(url=url_r, headers=headers, meta=meta_r)
                items = data['items']
                if items != None or items != []:
                    for i in items:
                        shop_id = i.get("shopid")
                        goods_id = i.get("itemid")
                        name = i.get("name")
                        price = i.get("price")  #价格
                        if price:
                            price = price/100000
                        currency = i.get("currency")  # 币种
                        historical_sold = i.get("historical_sold")  # 历史销量
                        sales_num = i.get("sold")
                        stock = i.get("stock")  # 库存
                        item_rating = i.get("item_rating")
                        rating_star = ""
                        if item_rating:
                            rating_star = item_rating.get('rating_star')  # 评分
                        item_status = i.get("item_status")  # 商品状态
                        show_free_shipping = i.get("show_free_shipping")  # 免邮
                        brand = i.get("brand")  # 品牌
                        location = i.get("shop_location")
                        view_count = i.get("view_count")
                        item = GmWorkItem()
                        item["shop_id"] = shop_id
                        item["goods_id"] = goods_id
                        item["name"] = name
                        item["price"] = price
                        item["currency"] = currency
                        item["total_num"] = historical_sold#历史销量
                        item["sales_num"] = sales_num
                        item["stock"] = stock
                        item["rating_star"] = rating_star
                        item["item_status"] = item_status
                        item["show_free_shipping"] = show_free_shipping
                        item["brand"] = brand
                        item["cid"] = match_id
                        item["url"] = url
                        item["location"] = location
                        item["view_count"] = view_count
                        item["pipeline_level"] = "list"
                        yield item
                        shop_url = self.shop_url.format(shop_id) #goods详情页
                        yield scrapy.Request(url=shop_url,headers=headers,callback=self.parse_shop,meta={'shop_id': shop_id})
                else:
                    print("为空：{}".format(url))
            except Exception as e:
                print(e)
                yield self.try_again(response, match_id=match_id, page=page)
        else:
            print("无效：{}".format(url))
            yield self.try_again(response,match_id=match_id,page=page)


    def parse_shop(self, response):
        url = response.url
        youxiao = re.search('("error_msg":null)',response.text)
        shop_id = response.meta.get("shop_id")
        if youxiao:
            item_s = GmWorkItem()
            item_s["key"] = shop_id
            item_s["pipeline_level"] = "店铺信息"
            item_s["source_code"] = response.text
            yield item_s
            try:
                items = json.loads(response.text)
                data = items.get("data")
                if data:
                    name = data.get("name")
                    description = data.get("description")
                    country = data.get("country")
                    place = data.get("place")
                    item_count = data.get("item_count")
                    rating_star = data.get("rating_star")
                    shop_location = data.get("shop_location")
                    follower_count = data.get("follower_count")#粉丝数
                    rating_good = data.get("rating_good")#好评数
                    rating_bad = data.get("rating_bad")# 差评数
                    cancellation_rate = data.get("cancellation_rate")# 退货率

                    item = GmWorkItem()
                    item["shop_id"] = shop_id
                    item["name"] = name
                    item["description"] = description
                    item["country"] = country
                    item["place"] = place
                    item["follower_count"] = follower_count
                    item["rating_good"] = rating_good
                    item["rating_bad"] = rating_bad
                    item["cancellation_rate"] = cancellation_rate
                    item["url"] = url
                    item["item_count"] = item_count
                    item["rating_star"] = rating_star
                    item["shop_location"] = shop_location
                    item["pipeline_level"] = "店铺信息"
                    yield item
            except Exception as e:
                print(e)
                yield self.try_again(response, shop_id=shop_id, pipeline_level="店铺信息")
        else:
            print("无效：{}".format(url))
            yield self.try_again(response, shop_id=shop_id, pipeline_level="店铺信息")


    def try_again(self,rsp,**kwargs):
        max_num = 4
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num < max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request
        else:
            request = rsp.request
            request.meta["try_num"] = 0
            obj = request_to_dict(request, self)
            data = picklecompat.dumps(obj)
            try:
                self.server.lpush(self.error_key, data)
            except Exception as e:
                print(e)
            # item_e = GmWorkItem()
            # item_e["error_id"] = 1
            # for i in kwargs:
            #     item_e[i] = kwargs[i]
            # return item_e

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
