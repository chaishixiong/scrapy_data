# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
import redis,json

class JdthSpider(RedisSpider):
    name = 'jd_th'
    allowed_domains = ['jd.co.th']
    start_urls = ['']
    redis_key = "jd_th:start_url"
    server1 = redis.Redis(host='192.168.0.226', port=5208, decode_responses=True)
    error_key = "jd_th:error_url"
    area_num = [(10001,21000),(1000000,1004000)]

    def start_requests(self):
        url = "http://www.baidu.com"
        yield scrapy.Request(url=url, method="GET",callback=self.seed_request)

    def seed_request(self,response):
        for i in self.area_num:
            for j in range(i[0],i[1]):
                vender_id = str(j)
                url = "https://m.jd.co.th/shop/-{}.html?pt=sd#/ShopDetail".format(vender_id)
                headers = self.get_headers(1)
                yield scrapy.Request(url=url,method="GET",callback=self.shop_saomiao,headers=headers,meta={"vender_id":vender_id})

    def shop_saomiao(self,response):
        vender_id = response.meta.get("vender_id")
        match = re.search("shop-name|ไม่พบหน้าเว็บที่คุณร้องขอ",response.text)
        if match:
            item_s = GmWorkItem()
            item_s["vender_id"] = vender_id
            item_s["source_code"] = response.text
            item_s["pipeline_level"] = "shop_info"
            yield item_s
            headers = self.get_headers(2)
            shop_name = response.css(".cell.shop-name").xpath("./text()").get()
            info = response.css(".details-item").xpath("./a")
            company = ""
            shop_about = ""
            open_time = ""
            for i in info:
                name = i.xpath("./span[1]/text()").get()
                value = i.xpath("./span[2]/text()").get()
                if "บริษัทที่ชื่อ" in name:
                    company = value
                elif "เกี่ยวกับผู้ขาย" in name:
                    shop_about = value
                elif "เวลาในการสร้าง" in name:
                    open_time = value
            if shop_name:
                item = GmWorkItem()
                item["vender_id"] = vender_id
                item["shop_name"] = shop_name
                item["company"] = company
                item["shop_about"] = shop_about
                item["open_time"] = open_time
                item["pipeline_level"] = "shop_info"
                yield item

                page_num = 1
                url = "https://m.jd.co.th/shop/search/searchWareAjax.json"
                data = "venderId={}&keyword=&pageIdx={}&searchSort=0&cateId=&clickSku=&skus=".format(vender_id,page_num)
                headers["referer"] = "https://m.jd.co.th/shop/{}.html".format(vender_id)
                yield scrapy.Request(url=url, method="post",callback=self.shop_goods, body=data,headers=headers,meta={"vender_id":vender_id,"first_page":True})
        else:
            self.try_again(response)
    def shop_goods(self,response):
        meta = response.meta
        vender_id = meta.get("vender_id")
        first_page = meta.get("first_page")
        category_list = meta.get("category_list",[])

        match = re.search('"success":true',response.text)
        if match:
            item_s = GmWorkItem()
            item_s["vender_id"] = vender_id
            item_s["source_code"] = response.text
            yield item_s
            headers = self.get_headers(2)
            url = "https://m.jd.co.th/shop/search/searchWareAjax.json"
            data_json = json.loads(response.text)
            results = data_json.get("results")
            totalPage = results.get("totalPage",0)#页数
            totalCount = results.get("totalCount")
            wareInfo = results.get("wareInfo",[])
            if first_page:
                categorys = results.get("category",[])#类目
                for category in categorys:
                    category_id = category.get("id")
                    category_title = category.get("title")
                    category_list.append({category_id:category_title})
                for i in range(2,totalPage+1):
                    data = "venderId={}&keyword=&pageIdx={}&searchSort=0&cateId=&clickSku=&skus=".format(vender_id,i)
                    headers["referer"] = "https://m.jd.co.th/shop/{}.html".format(vender_id)
                    yield scrapy.Request(url=url, method="post", callback=self.shop_goods, body=data, headers=headers,
                                         meta={"vender_id": vender_id,"category_list":category_list})
                items = GmWorkItem()
                items["vender_id"] = vender_id
                items["total_num"] = totalCount
                items["categorys"] = category_list
                items["pipeline_level"] = "shop_info_s"
                yield items

            for i in wareInfo:
                wareId = i.get("wareId")
                wname = i.get("wname")
                imageurl = i.get("imageurl")
                jdPrice = i.get("jdPrice")
                opPrice = i.get("opPrice")
                good = i.get("good")
                comment_num = i.get("totalCount")
                item = GmWorkItem()
                item["vender_id"] = vender_id
                item["total_num"] = totalCount
                item["categorys"] = category_list
                item["goods_id"] = wareId
                item["goods_name"] = wname
                item["img_url"] = imageurl
                item["price"] = jdPrice
                item["original_price"] = opPrice
                item["comment"] = good
                item["comment_num"] = comment_num
                yield item


    def try_again(self,rsp):
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

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
pragma: no-cache
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
        else:
            headers = '''accept: */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
content-type: application/x-www-form-urlencoded; charset=UTF-8
origin: https://m.jd.co.th
pragma: no-cache
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1
x-requested-with: XMLHttpRequest
Host: m.jd.co.th'''
        return headers_todict(headers)
