# -*- coding: utf-8 -*-
import scrapy
from tools.tools_request.spider_class import RedisSpiderTryagain
from nriat_spider.items import AmazonItem
from tools.tools_request.header_tool import headers_todict
import re
from twisted.web.http_headers import Headers as TwistedHeaders

TwistedHeaders._caseMappings.update({
    b'Host': b'host',
    b'User-Agent': b'user-agent',
    b'accept-encoding': b'accept-encoding',
    b'accept': b'accept',
    b'Connection': b'connection',
    b'accept-language': b'accept-language',
    b'upgrade-insecure-requests': b'upgrade-insecure-requests'
})

class AmazonShopGoods(RedisSpiderTryagain):
    name = 'amazon_shopinfo'
    allowed_domains = ['amazon.com']
    start_urls = ['http://www.amazon.com/']
    redis_key = "amazon_shopinfo:start_url"#添加file文件加入redis
    error_key = "amazon_shopinfo:error_url"
    custom_settings = {"CONCURRENT_REQUESTS":2,"CHANGE_IP_NUM":100,"DOWNLOADER_MIDDLEWARES":{
    'nriat_spider.middlewares.IpChangeDownloaderMiddleware': 20,
    'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,
    'nriat_spider.middlewares.UserAgentChangeDownloaderMiddleware': 22,
}}
    headers = '''Host: www.amazon.com
User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36
accept-encoding: gzip, deflate, br
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Connection: keep-alive
accept-language: zh-CN,zh;q=0.9
upgrade-insecure-requests: 1'''

    def make_requests_from_url(self, seed):
        id = seed.strip()
        url = "https://www.amazon.com/sp?ie=UTF8&isCBA=&language=en_US&seller={}&tab=&vasStoreID=".format(id)
        return scrapy.Request(url=url, method="GET", headers=headers_todict(self.headers),meta={"id":id,"proxy":"127.0.0.1:8080"})

    def parse(self, response):
        youxiao = re.search("(Detailed Seller|errors/404)",response.text)
        id = response.meta.get("id")
        if youxiao:
            shop_id = id
            text = response.text
            shop_name = ""
            shop_info = ""
            company = ""
            country = ""
            postcode = ""
            shop_name_match = re.search('sellerName">([^<]*)</h1>',text)
            if shop_name_match:
                shop_name = shop_name_match.group(1)
            shop_info_match = re.search('"about-seller-text">([^/]*)</span>',text)
            if shop_info_match:
                shop_info = shop_info_match.group(1)
            company_match = re.search('Business Name:</span>([^<]*)</span>',text)
            if company_match:
                company = company_match.group(1)
            company_address = response.xpath('//span[contains(text(),"Business Address")]/following-sibling::ul[1]/li[1]').xpath("string(.)").get("").strip()
            country_match = re.search('Business Address:</span>.*?(CN).*?</ul>',text)
            if country_match:
                country = country_match.group(1)
            postcode_match = re.search('Business Address:</span>.*?>(\d+)<.*?</ul>',text)
            if postcode_match:
                postcode = postcode_match.group(1)
            html = response.xpath('//span[contains(text(),"Business Address")]/following-sibling::ul[1]').xpath("string(.)").get("").strip()
            goodrate_mouth = response.css("#feedback-summary-table").xpath("./tr[2]/td[2]").xpath("string(.)").get("").strip()
            middlerate_mouth = response.css("#feedback-summary-table").xpath("./tr[3]/td[2]").xpath("string(.)").get("").strip()
            badrate_mouth = response.css("#feedback-summary-table").xpath("./tr[4]/td[2]").xpath("string(.)").get("").strip()
            comment_mouth = response.css("#feedback-summary-table").xpath("./tr[5]/td[2]").xpath("string(.)").get("").strip()
            comment_mouth = comment_mouth.replace(",","")
            goodrate_quarterly = response.css("#feedback-summary-table").xpath("./tr[2]/td[3]").xpath("string(.)").get("").strip()
            middlerate_quarterly = response.css("#feedback-summary-table").xpath("./tr[3]/td[3]").xpath("string(.)").get("").strip()
            badrate_quarterly = response.css("#feedback-summary-table").xpath("./tr[4]/td[3]").xpath("string(.)").get("").strip()
            comment_quarterly = response.css("#feedback-summary-table").xpath("./tr[5]/td[3]").xpath("string(.)").get("").strip()
            comment_quarterly = comment_quarterly.replace(",","")
            goodrate_year = response.css("#feedback-summary-table").xpath("./tr[2]/td[4]").xpath("string(.)").get("").strip()
            middlerate_year = response.css("#feedback-summary-table").xpath("./tr[3]/td[4]").xpath("string(.)").get("").strip()
            badrate_year = response.css("#feedback-summary-table").xpath("./tr[4]/td[4]").xpath("string(.)").get("").strip()
            comment_year = response.css("#feedback-summary-table").xpath("./tr[5]/td[4]").xpath("string(.)").get("").strip()
            comment_year = comment_year.replace(",","")
            goodrate_total = response.css("#feedback-summary-table").xpath("./tr[2]/td[5]").xpath("string(.)").get("").strip()
            middlerate_total = response.css("#feedback-summary-table").xpath("./tr[3]/td[5]").xpath("string(.)").get("").strip()
            badrate_total = response.css("#feedback-summary-table").xpath("./tr[4]/td[5]").xpath("string(.)").get("").strip()
            comment_total = response.css("#feedback-summary-table").xpath("./tr[5]/td[5]").xpath("string(.)").get("").strip()
            comment_total = comment_total.replace(",","")
            province = ""
            city = ""
            county = ""
            main_sales = ""
            average_price = ""
            item_s = AmazonItem()
            item_s["id"] = id
            item_s["source_code"] = response.text
            yield item_s
            item = AmazonItem()
            item["shop_id"] = shop_id
            item["shop_name"] = shop_name
            item["shop_info"] = shop_info
            item["company"] = company
            item["company_address"] = company_address
            item["country"] = country
            item["postcode"] = postcode
            item["html"] = html
            item["goodrate_mouth_info"] = goodrate_mouth
            item["middlerate_mouth_info"] = middlerate_mouth
            item["badrate_mouth_info"] = badrate_mouth
            item["comment_mouth_info"] = comment_mouth
            item["goodrate_quarterly"] = goodrate_quarterly
            item["middlerate_quarterly"] = middlerate_quarterly
            item["badrate_quarterly"] = badrate_quarterly
            item["comment_quarterly"] = comment_quarterly
            item["goodrate_year"] = goodrate_year
            item["middlerate_year"] = middlerate_year
            item["badrate_year"] = badrate_year
            item["comment_year"] = comment_year
            item["goodrate_total"] = goodrate_total
            item["middlerate_total"] = middlerate_total
            item["badrate_total"] = badrate_total
            item["comment_total"] = comment_total
            item["province"] = province
            item["city"] = city
            item["county"] = county
            item["main_sales"] = main_sales
            item["average_price"] = average_price
            yield item
        else:
            try_result = self.try_again(response)
            yield try_result