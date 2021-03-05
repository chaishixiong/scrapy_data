# -*- coding: utf-8 -*-
import scrapy
import re
import json
from ..items import AllegroItem
from tools.tools_request.spider_class import RedisSpiderTryagain


class AllegroGoodsSpider(RedisSpiderTryagain):
    name = 'allegro_goods'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_goods:start_url"
    error_key = "allegro_goods:error_url"
    headers = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    }
    custom_settings = {"CHANGE_IP_NUM":50,"REDIRECT_ENABLED":True}

    def make_requests_from_url(self, url):
        url = 'https://allegro.pl/oferta/zestaw-czyszczacy-9w1-do-aparatu-optyki-sciereczka-{}'.format(url)
        return scrapy.Request(url=url, callback=self.parse, headers=self.headers, meta={'url': url})

    def parse(self, response):
        youxiao = re.search("(opboxContext|offerTitle)", response.text)
        if youxiao:
            # item_s = AllegroItem()
            # item_s["source_code"] = response.text
            # yield item_s
            match = re.search('"LUo64bt1RQOuwIphdVaomw==Z6xO7DZsQCOjqrGW72FzMQ==">(.*?)</script>', response.text)
            if match:
                data = match.group(1)
                data = json.loads(data)
                # 店铺id
                try:
                    shop_id = data.get('transactionSection', {})
                    shop_id = shop_id.get('precartData', {}).get('sellerId', {})
                except:
                    shop_id = ''
                # 超级店铺
                try:
                    shop_super = data.get('offerTitle', {})
                    shop_super = shop_super.get('superSellerActive', {})
                except:
                    shop_super = ''
                # 店铺名称
                try:
                    shop_name = data.get('offerTitle', {})
                    shop_name = shop_name.get('sellerName', {})
                except:
                    shop_name = ''
                # 好评率
                try:
                    positive_feedback = data.get('offerTitle', {})
                    positive_feedback = positive_feedback.get('sellerRating', {})
                except:
                    positive_feedback = ''
                # 评论数量
                try:
                    positive_number = data.get('metaData', {})
                    positive_number = positive_number.get('dataLayer', {}).get('idCategory', {})
                except:
                    positive_number = ''
                # 产品评分数量
                try:
                    ratingCountLabel = data.get('productRating', {})
                    ratingCountLabel = ratingCountLabel.get('ratingCountLabel', {})
                except:
                    ratingCountLabel = ''
                # 货币类型
                try:
                    huobi_type = data.get('notifyAndWatch', {})
                    huobi_type = huobi_type.get('sellingMode', {}).get('buyNow', {}).get('price', {}).get('sale', {}).get(
                        'currency', {})
                except:
                    huobi_type = ''

                items = AllegroItem(shop_id=shop_id, shop_super=shop_super, shop_name=shop_name,
                                    positive_feedback=positive_feedback,
                                    positive_number=positive_number, ratingCountLabel=ratingCountLabel,
                                    huobi_type=huobi_type)

                yield items
        else:
            try_result = self.try_again(response)
            yield try_result