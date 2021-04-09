# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re,redis
from scrapy.selector import Selector
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class NeweggGoodsSpider(RedisSpider):
    name = 'newegg_goods'
    allowed_domains = ['newegg.com']
    start_urls = ['']
    redis_key = "newegg_goods:start_url"
    custom_settings = {'CONCURRENT_REQUESTS': 2,"CHANGE_IP_NUM": 40,"SCHEDULER_QUEUE_CLASS": 'scrapy_redis.queue.FifoQueue',"REDIRECT_ENABLED":True}
    # server = redis.Redis(host='192.168.0.225', port=5208, decode_responses=True)
    error_key = "newegg_goods:error_url"


    def start_requests(self):
        headers = self.get_headers(1)
        headers["referer"] = "https://www.newegg.com/"
        url = "https://www.newegg.com/Common/Ajax/Navigation.aspx?callback=Web.Template.RolloverMenu2015.JsonpCallBack"
        yield scrapy.Request(url=url,headers=headers,callback=self.sort_all)

    def sort_all(self,response):
        if "RolloverMenu2015" in response.text:
            headers=self.get_headers(1)
            headers["referer"] = "https://www.newegg.com/"
            sort_urls = response.css(".main-nav-subItem").xpath("./a")
            match = re.search('JsonpCallBack\("([\S\s]*)"\)',response.text)
            html_str = ""
            if match:
                html_str = match.group(1)
            html_str = html_str.replace('\\"','"')
            selector = Selector(text=html_str)

            if not sort_urls:
                sort_urls = selector.css(".main-nav-subItem").xpath(".//ul[@class='main-nav-third-categories']/li/a")
            for i in sort_urls:
                url = i.xpath("./@href").get()
                if not url.startswith("https:"):
                    url = re.sub(".*?//","https://",url)
                name = i.xpath("./text()").get()
                item = GmWorkItem()
                item["pipeline_level"] = "sort"
                item["name"] = name
                yield item
                yield scrapy.Request(url=url,headers=headers,callback=self.detail_data,meta={"sort_name":name,"first":True})
        else:
            try_result = self.try_again(response)
            yield try_result

    def detail_data(self,response):
        sort = response.meta.get("sort_name")
        first = response.meta.get("first")
        req_url = response.request.url
        match = re.search('baBreadcrumbTop|item-container|find the SubCategory|check your',response.text)
        if match:
            item_s = GmWorkItem()
            item_s["source_code"] = response.text
            yield item_s
            headers =self.get_headers(1)
            goods_list = response.css(".item-container")
            for i in goods_list:
                url = i.xpath("./div[@class='item-info']/a/@href").get()
                name_goods = i.xpath("./div[@class='item-info']/a/text()").get()
                brand = i.xpath(".//div[@class='item-branding']/a/img/@title").get()
                price = i.xpath(".//li[@class='price-current ']").xpath("string(.)").get("")
                if not price:
                    price = i.xpath(".//li[@class='price-current']").xpath("string(.)").get("")
                price = re.sub("[^\d\.]","",price)
                goods_id = i.xpath(".//div[@class='item-stock']/@id").get("")
                goods_id = goods_id.replace("stock_","")
                size = ""
                type = ""
                color = ""
                age = ""
                shop_url = ""
                shop_name = ""
                item_featuresb = i.xpath(".//ul[@class='item-features']/li")
                for j in item_featuresb:
                    name = j.xpath("./strong/text()").get()
                    value = j.xpath("./text()").get()
                    if "Size" in name:
                        size = value
                    elif "Type" in name:
                        type = value
                    elif "Color" in name:
                        color = value
                    elif "Age" in name:
                        age = value
                    elif "Policy" in name:
                        shop_url = j.xpath("./a/@href").get("")
                        match = re.search("com/(.*?)/about",shop_url)
                        if match:
                            shop_name = match.group(1)
                item = GmWorkItem()
                item["sort"] = sort
                item["url"] = url
                item["name"] = name_goods
                item["brand"] = brand
                item["price"] = price
                item["goods_id"] = goods_id
                item["size"] = size
                item["type"] = type
                item["color"] = color
                item["age"] = age
                item["shop_url"] = shop_url
                item["shop_name"] = shop_name
                yield item
                if first:
                    page_str = response.css(".list-tool-pagination-text").xpath("./strong").xpath("string(.)").get("")
                    match1 = re.search("/(\d+)",page_str)
                    if match1:
                        page_num = int(match1.group(1))
                        for i in range(2,page_num+1):
                            url = req_url.replace("?","/Page-{}?".format(i))
                            yield scrapy.Request(url=url, headers=headers, callback=self.detail_data,
                                                 meta={"sort_name": sort})
        else:
            try_result = self.try_again(response)
            yield try_result


    def try_again(self,rsp,**kwargs):
        max_num = 3
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
        return headers_todict(headers)
