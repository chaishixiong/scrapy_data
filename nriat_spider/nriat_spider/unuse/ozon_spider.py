#coding:utf-8
import re
import scrapy
from tqdm import tqdm
import json
from nriat_spider.items import Ozon1Item
from tools.tools_request.spider_class import RedisSpiderTryagain

class OnzonSpiderSpider(RedisSpiderTryagain):
    name = 'ozon_spider'
    allowed_domains = ['ozon.ru']
    # start_urls = ['https://www.ozon.ru/']
    redis_key = 'ozon1:start_url'
    error_key = "ozon1:error_url"


    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'Origin': 'https://www.ozon.ru',
        'cookie':'__Secure-ab-group=20; __Secure-session-id=77YVlv-KQdGoeaiV6yQNdw; abGroup=20; SessionID=77YVlv-KQdGoeaiV6yQNdw; xcid=271a80721af53f6324f3afc53e16359e; nlbi_1101384=cOmpf0fV9hdme2kBsyIZFQAAAAAGlVDV3K9rKwJ8DUE+Tztr; visid_incap_1101384=ADKbpzTSQtahvMMr0xhwCF9u8V4AAAAAQUIPAAAAAAD+bmlLXkDyRRjxSUDkZv7Z; _gcl_au=1.1.285806398.1592880748; _ga=GA1.2.1925586689.1592880749; isBuyer=0; cnt_of_orders=0; tmr_lvid=3af4d4fc174c722949662e598d9e92fb; tmr_lvidTS=1592880752769; __exponea_etc__=669ae053-8909-4d07-9cd4-663a1317d3ec; _fbp=fb.1.1592880765554.409754061; visid_incap_2317293=pDJ8sTJvSj2VtPVupXxK8ied8V4AAAAAQUIPAAAAAADMqI8k9KB7TJP625TgCNKx; nlbi_2317293=uf/NCbA16xmRUt+ELUtXRAAAAAA8lI7pBlsbjiIfKNkwPwSu; incap_ses_408_1101384=XOItKLsmhBLv+GiR64GpBeug8V4AAAAAp8du/prthiAAu2S5Hvll2g==; incap_ses_47_2317293=grMZAmED8xgT0lnDivqmABjR8V4AAAAAvOKKZU4WJT2mYinhTnhaQA==; incap_ses_456_1101384=lD6tGSB4emFoxYJ7owlUBrjS8V4AAAAA59EaFam/XeAu8/UBHYA0Yw==; incap_ses_457_1101384=v/ahMAoviAe53O0fIpdXBsLS8V4AAAAA2bihK3iqzpn0mNcdgtm8Yw==; incap_ses_535_1101384=19dUR6FT51MH5OpXsbNsB3ve8V4AAAAA2o3VqWrj/m2d1W0FnkA0/Q==; incap_ses_47_1101384=FCF8GMSfKBDmAW/DivqmAKDe8V4AAAAAZOrvBXLOzb+buO7WUUgK+g==; incap_ses_458_1101384=1GXARV09q0JZFD/JmSRbBmbt8V4AAAAAFJ6ly7tznFvllMdxLsSLxw==; incap_ses_728_1101384=s4BcZA9EHyA/GVk+KWAaCmT08l4AAAAAqq9vkdixrl/IAMSEoOyaBg==; incap_ses_151_1101384=T625etMDXyCChiL7G3YYAnr/8l4AAAAAvVrzboLAoMHZ/CHMR/jcmw==; incap_ses_374_1101384=CQFqIU6aWmVVHaoOB7cwBfww814AAAAADsPTPbcaziBlEQ4j0fFypQ==; incap_ses_453_1101384=hvoUc/VAwShibcqOLmFJBoM1+F4AAAAAlTOMrk77g/HrgLLYkFQzQA==; incap_ses_730_1101384=cnqZPWI6v1wZdODhKHshCvZL+F4AAAAAinN36CmckzYZeRz+1+Li9g==; incap_ses_875_1101384=UlEUcHKQOkJZXA3i4Z8kDGvA+V4AAAAAhK4w6FD0wPx61ar5/KwMTA==; _gid=GA1.2.811174674.1593426242; h_prem4=false; incap_ses_534_1101384=jUROQD1IGzKm3U4EPCZpB7iT+l4AAAAAABAnv0gYUqNkJjgt51scUw==; __Secure-access-token=2.0.77YVlv-KQdGoeaiV6yQNdw.20.lscMBQAAAABe8W5fAAAAAKN3ZWKgAICQ..20200630032653.8C8_WfX1KgKvmnXORTu1pmBY0b7JDX_7i7roVt-3MKM; __Secure-refresh-token=8jgmphWwdIT2k9CQGpp2_JHCHinw42tonYhag-x263BfXGr9tGgwDnpNc8xDdXRNRzgZH5aAtQZfSkS48YYe0hgELnQ2hG5NZ_WMMuoXppKrK2cXezrDZBK0kQbolw6HQb-11ddONRWXSWuBDl2ZLkK0vle9MYOYf-Bj-89WWElgXfONN81ss0oKkNNvq-CtEVJkAj3EGGJQaxRGP-5P3rn9ghPwS_vHkYkhvTrOmraKeq7o0MkCfDG_D5cAvYB6EGIlz1b0JgsPP_U0a9tPuld5CY5ZfoK-lcijBS0TAYJUys1UQwgKnDmxPy_ZBu6R5F-vEE_oBSOoUZ65GyvZGwcWdBMFBkbNsFnuvYceT--9yv9sAlZQ8aIjTNSKoQs78qLV_cpFzb-ue4yDMHKfDjsa5WFRJK3aVuYepfZzK39o3IZPjT_C4ROHRYHaR_1djyIbENCizXM; access_token=2.0.77YVlv-KQdGoeaiV6yQNdw.20.lscMBQAAAABe8W5fAAAAAKN3ZWKgAICQ..20200630032653.8C8_WfX1KgKvmnXORTu1pmBY0b7JDX_7i7roVt-3MKM; refresh_token=8jgmphWwdIT2k9CQGpp2_JHCHinw42tonYhag-x263BfXGr9tGgwDnpNc8xDdXRNRzgZH5aAtQZfSkS48YYe0hgELnQ2hG5NZ_WMMuoXppKrK2cXezrDZBK0kQbolw6HQb-11ddONRWXSWuBDl2ZLkK0vle9MYOYf-Bj-89WWElgXfONN81ss0oKkNNvq-CtEVJkAj3EGGJQaxRGP-5P3rn9ghPwS_vHkYkhvTrOmraKeq7o0MkCfDG_D5cAvYB6EGIlz1b0JgsPP_U0a9tPuld5CY5ZfoK-lcijBS0TAYJUys1UQwgKnDmxPy_ZBu6R5F-vEE_oBSOoUZ65GyvZGwcWdBMFBkbNsFnuvYceT--9yv9sAlZQ8aIjTNSKoQs78qLV_cpFzb-ue4yDMHKfDjsa5WFRJK3aVuYepfZzK39o3IZPjT_C4ROHRYHaR_1djyIbENCizXM; __Secure-token-expiration=2020-06-30T06:26:53+03:00; token_expiration=2020-06-30T06:26:53+03:00; __exponea_time2__=-1.3577067852020264; incap_ses_197_1101384=ii4pdMgqFQvxakxsnOK7AqCh+l4AAAAAkGHBa7YBZKkNVFWxHW7nvg==; tmr_detect=0%7C1593483705349; RT="z=1&dm=ozon.ru&si=f2bb5f22-f397-4448-a7ff-64248c2c79a8&ss=kc195dmj&sl=6&tt=136sp&bcn=%2F%2F173e2544.akstat.io%2F&ld=1xbli&nu=arde5zk&cl=1xhgl&ul=207rn"; tmr_reqNum=200',
    }
    headers_cat = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
    }
    custom_settings = {
        "CHANGE_IP_NUM": 1000, "CONCURRENT_REQUESTS": 8
    }
    def start_requests(self):
        url = "https://www.ozon.ru/category/detskie-tovary-7000/"
        urls = ["https://www.ozon.ru/category/retro-13105/","https://www.ozon.ru/category/disko-13104/","https://www.ozon.ru/category/brit-pop-13106/"]
        for i in urls:
            yield scrapy.Request(url=i,headers=self.headers_cat)#,callback=self.get_page

    def get_page(self,response):
        youxiao = "__ozon"
        if youxiao in response.text:
            ls = response.xpath('//*[@id="__ozon"]/div/div[1]/header/div[1]/div[2]/div/div[2]/div/div[1]/div/a/@href').getall()
            for each in ls:
                ls1_each = each.split('-')[-1].split('/')[0]
                if ls1_each:
                    ls2 = 'https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=%2Fcategory%2F{}%2F%3Fpage_changed%3Dtrue'.format(ls1_each)
                    yield scrapy.Request(url=ls2, headers=self.headers_cat)

    def get_page2(self,response):
        youxiao = "widgetStates"
        if youxiao in response.text:
            categories = response.json()['categories']
            for i in categories:
                url_detail = i['url']
                url = 'https://www.ozon.ru' + url_detail
    #                     ls2_each = 'https://www.ozon.ru/webapi/catalog-menu-api.bx/menu/category/child/v1?categoryId=' + \
    #                                url_detail.split('-')[-1].split('/')[0]
    #                     response3 = requests.get(ls2_each, headers=headers)
    #
    #                     for m in response3.json()['categories']:
    #                         url1 = m['url']
    #
    #                         url2 = 'https://www.ozon.ru' + url1
    #
    #                         print(url2)
    #                         print('====================================')
    #                         with open(r'cat_url_202012.txt', 'a', encoding='utf-8') as f:
    #                             f.write(url2 + '\n')
    #             i = i.replace('\n', '')
    #             page = 1
    #             url = i + '?page='
    #             url1 = url + str(page)
    #             yield scrapy.Request(url=url1,callback=self.parse,headers=self.headers, meta={'host': url, 'page': page})
    #  翻页
    def parse(self, response):
        host = response.meta.get('host')
        page = response.meta.get('page')
        # print(response.text)
        maxpage = re.findall(r'"totalPages":(\d+)},', response.text)[0]
        # print(page, maxpage)
        json_code = re.findall(r'id="state-searchResultsV2-.+?>(.+?)</script>', response.text)
        if json_code != []:
            json_code = json_code[0]

            data = json.loads(json_code)
            items = data['items']
            source_code = items
            item2 = Ozon1Item(source_code=source_code)
            yield item2

            if items != None or items != []:
                for i in items:
                    # print(i)
                    try:
                        shop_id = i['cellTrackingInfo']['id']
                    except:
                        shop_id = ''

                    # 商品名
                    try:
                        good_name = i['cellTrackingInfo']['title']
                    except:
                        good_name = ''

                    # 现价
                    try:
                        new_price = i['cellTrackingInfo']['finalPrice']
                    except:
                        new_price = ''

                    # 原价
                    try:
                        old_price = i['cellTrackingInfo']['price']
                    except:
                        old_price = ''

                    # 折扣
                    try:
                        discount = i['cellTrackingInfo']['discount']
                    except:
                        discount = ''

                    #  类别
                    try:
                        leibie = i['cellTrackingInfo']['category']
                    except:
                        leibie = ''

                    # 评论数
                    try:
                        comment_nums = i['templateState'][0]['components'][1]['components'][0]['components'][3]['commentsCount']
                    except:
                        comment_nums = ''

                    item1 = Ozon1Item(shop_id=shop_id, good_name=good_name, new_price=new_price,
                                      old_price=old_price,
                                      discount=discount, leibie=leibie, comment_nums=comment_nums)

                    yield item1

                if page <= int(maxpage):
                    next_url = host + str(page+1)
                    print(next_url)

                    yield scrapy.Request(url=next_url,callback=self.parse,headers=self.headers,meta={'host':host,'page':page+1})