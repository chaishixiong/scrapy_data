# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
import json
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class AllegroSpider(RedisSpider):
    name = 'allegro_good'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_good:start_url"
    # seed_file = r"X:\数据库\allegro\{allegro_shopid}[good_url].txt"
    # seed_file = r"W:\lxd\采集数据\allegro\202010\allegro_spider-data_合并.txt_去重.txt[F2].txt"
    custom_settings = {"CHANGE_IP_NUM":20,"CONCURRENT_REQUESTS":4,"REDIRECT_ENABLED":True}
    error_key = "allegro_good:error_url"



    headers = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    }

    def start_requests(self):
        with open(r'W:\lxd\采集数据\allegro\202010\allegro_spider-data_合并.txt_去重.txt[F2].txt', 'r', encoding='utf-8') as f:
            for i in f:
                i = i.replace('\n', '')
                url = 'https://allegro.pl/oferta/zestaw-czyszczacy-9w1-do-aparatu-optyki-sciereczka-{}'.format(i)
                print('*******************', url)
                yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, meta={'url': url})


    def parse(self, response):
        youxiao = re.search("(opboxContext|offerTitle)", response.text)
        url = response.request.url
        if youxiao:
            item_s = GmWorkItem()
            item_s["url"] = url
            item_s["source_code"] = response.text
            yield item_s

            data = re.findall('data-serialize-box-name="summary">(.*?)</script>', response.text)[0]
            # print(data)
            data = json.loads(data)
            # 店铺id
            try:
                shop_id = data.get('transactionSection', {})
                shop_id = shop_id.get('precartData', {}).get('sellerId', {})

                print(shop_id)
            except:
                shop_id = ''

            # 超级店铺
            try:
                shop_super = data.get('offerTitle', {})
                shop_super = shop_super.get('superSellerActive', {})
                print(shop_super)
            except:
                shop_super = ''

            # 店铺名称
            try:
                shop_name = data.get('offerTitle', {})
                shop_name = shop_name.get('sellerName', {})
                print(shop_name)
            except:
                shop_name = ''
            # 好评率
            try:
                positive_feedback = data.get('offerTitle', {})
                positive_feedback = positive_feedback.get('sellerRating', {})
                print(positive_feedback)
            except:
                positive_feedback = ''

            # 评论数量
            try:
                positive_number = data.get('metaData', {})
                positive_number = positive_number.get('dataLayer', {}).get('idCategory', {})
                print(positive_number)
            except:
                positive_number = ''

            # 产品评分数量
            try:
                ratingCountLabel = data.get('productRating', {})
                ratingCountLabel = ratingCountLabel.get('ratingCountLabel', {})
                print(ratingCountLabel)
            except:
                ratingCountLabel = ''

            # 货币类型
            try:
                huobi_type = data.get('notifyAndWatch', {})
                huobi_type = huobi_type.get('sellingMode', {}).get('buyNow', {}).get('price', {}).get('sale',
                                                                                                      {}).get(
                    'currency', {})
                print(huobi_type)
            except:
                huobi_type = ''
            print('===================================================================')

            items = GmWorkItem(shop_id=shop_id, shop_super=shop_super, shop_name=shop_name,
                                positive_feedback=positive_feedback,
                                positive_number=positive_number, ratingCountLabel=ratingCountLabel,
                                huobi_type=huobi_type)

            yield items
        else:
            try_result = self.try_again(response, url=url)
            yield try_result

    def try_again(self,rsp,**kwargs):
        max_num = 5
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




