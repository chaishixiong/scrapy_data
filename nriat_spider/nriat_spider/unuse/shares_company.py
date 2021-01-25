# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class SharesSpider(RedisSpider):
    name = 'shares_company'
    allowed_domains = ['sina.com.cn']
    start_urls = ['https://finance.sina.com.cn/']
    redis_key = "shares_company:start_url"
    custom_settings = {"DOWNLOAD_DELAY":3}
    error_key = "shares_company:error_url"

    def start_requests(self):
        headers = self.get_headers(1)
        with open(r"D:\scrapy_seed\shares_seed.txt","r",encoding="utf-8") as f:
            for i in f:
                id = i.strip()
                url = "https://finance.sina.com.cn/realstock/company/{}/nc.shtml".format(id)
                #新浪财经url
                yield scrapy.Request(url=url,method="GET",headers=headers,meta={"id":id})


    def parse(self, response):
        youxiao = re.search("com_overview",response.text)
        id = response.meta.get("id")
        if youxiao:
            com_overview = response.css(".com_overview.blue_d")
            company = com_overview.xpath("./p[2]/text()").get()
            main_sales = com_overview.xpath("./p[4]/text()").get()
            phone = com_overview.xpath("./p[5]/text()").get()
            fax = com_overview.xpath("./p[6]/text()").get()
            creat_date = com_overview.xpath("./p[7]/text()").get()
            start_date = com_overview.xpath("./p[8]/text()").get()
            legal_person = com_overview.xpath("./p[9]/text()").get()
            general_manager = com_overview.xpath("./p[10]/text()").get()
            registered_capital = com_overview.xpath("./p[11]/text()").get()
            price = com_overview.xpath("./p[12]/text()").get()
            share_capital = com_overview.xpath("./p[13]/text()").get()
            circulating_shares = com_overview.xpath("./p[14]/text()").get()
            plate = com_overview.xpath("./p[15]/a/text()").getall()
            item = GmWorkItem()
            item["id"] = id
            item["company"] = company
            item["main_sales"] = main_sales
            item["phone"] = phone
            item["fax"] = fax
            item["creat_date"] = creat_date
            item["start_date"] = start_date
            item["legal_person"] = legal_person
            item["general_manager"] = general_manager
            item["registered_capital"] = registered_capital
            item["price"] = price
            item["share_capital"] = share_capital
            item["circulating_shares"] = circulating_shares
            item["plate"] = "|".join(plate)
            yield item
        else:
            try_result = self.try_again(response)
            yield try_result


    def try_again(self,rsp):
        print("错误了")
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
                self.server.lpush(self.error_key,data)
            except Exception as e:
                print(e)

    def get_headers(self,type=1):
        if type == 1:
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: finance.sina.com.cn
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'''
        else:
            headers = '''accept: application/json
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
content-type: application/json;charset=UTF-8
origin: https://hotels.ctrip.com
pragma: no-cache
sec-fetch-mode: cors
sec-fetch-site: same-site
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36
Host: m.ctrip.com
'''
        return headers_todict(headers)
