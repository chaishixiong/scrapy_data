# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re


class AlibabgjSpider(RedisSpider):
    name = 'alibabgj_shop'
    allowed_domains = ['alibaba.com']
    start_urls = ['http://www.alibaba.com/']
    redis_key = "alibabgj_shop:start_url"
    headers = headers_todict('''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36''')

    file_name = r"X:\数据库\阿里巴巴国际站\alibaba_shopid_all.txt"
    def start_requests(self):
        url = "https://www.baidu.com"
        yield scrapy.Request(url=url, method="GET",callback=self.seed_requests, headers=self.headers,dont_filter=True)

    def seed_requests(self,response):
        with open(self.file_name,"r",encoding="utf-8") as f:
            for i in f:
                i = i.strip()
                url = "https://{}.alibaba.com/contactinfo.html".format(i)
                meta = {"key":i}
                yield scrapy.Request(url=url,method="GET",headers=self.headers,meta=meta)

    def parse(self, response):
        youxiao = re.search("(HTTP 404|Information|302 Found)",response.text)
        url = response.request.url
        key = response.meta.get("key")
        if youxiao:
            text = response.text
            item_s = GmWorkItem()
            item_s["key"] = key
            item_s["source_code"] = text
            yield item_s
            address_detail = ""
            company_name = ""
            val_judge = 0
            contact_table = response.css(".contact-table").xpath("./tr")
            if not contact_table:
                contact_table = response.css(".company-info-data.table").xpath("./tr")
                val_judge = 1
            for i in contact_table:
                name = i.xpath("./th").xpath("string(.)").get()
                if val_judge:
                    value = i.xpath("./td[2]").xpath("string(.)").get()
                else:
                    value = i.xpath("./td").xpath("string(.)").get()
                if name and "Address" in name:
                    address_detail = value
                if name and "Company Name" in name:
                    company_name = value
            country = ""
            province = ""
            city = ""
            address = ""
            zip = ""
            info_table = response.css(".info-table").xpath("./tr")
            if not info_table:
                info_table = response.css(".public-info").xpath("./dl")
                for i in range(len(info_table.xpath("./dt"))):
                    name = info_table.xpath("./dt[{}]".format(i+1)).xpath("string(.)").get()
                    value = info_table.xpath("./dd[{}]".format(i+1)).xpath("string(.)").get()
                    if name and "Country" in name:
                        country = value
                    if name and "Province" in name:
                        province = value
                    if name and "City" in name:
                        city = value
                    if name and "Zip" in name:
                        zip = value
                    if name and "Address" in name:
                        address = value
            else:
                for i in info_table:
                    name = i.xpath("./th").xpath("string(.)").get()
                    value = i.xpath("./td").xpath("string(.)").get()
                    if name and "Country" in name:
                        country = value
                    if name and "Province" in name:
                        province = value
                    if name and "City" in name:
                        city = value
                    if name and "Zip" in name:
                        zip = value
                    if name and "Address" in name:
                        address = value
            contact_people = response.css(".contact-name").xpath("./text()").get()
            if not contact_people:
                contact_people = response.css(".name").xpath("./text()").get()
            companyJoinYears = response.css(".join-year").xpath("./span/text()").get()
            company_type = response.css(".business-type").xpath("./text()").get()
            ordCnt6m = response.css(".transaction-number-value").xpath("./text()").get()
            ordAmt = response.css(".transaction-amount-value").xpath("./text()").get()
            if ordAmt:
                ordAmt = ordAmt.replace(",", "")
                ordAmt = ordAmt.replace("+", "")
            item = GmWorkItem()
            item["key"] = key
            item["url"] = url
            item["company_name"] = company_name
            item["address_detail"] = address_detail
            item["country"] = country
            item["province"] = province
            item["city"] = city
            item["address"] = address
            item["zip"] = zip
            item["contact_people"] = contact_people

            item["sales_money"] = ordAmt
            item["sales_num"] = ordCnt6m
            item["company_type"] = company_type
            item["keep_time"] = companyJoinYears
            yield item
            if response.status == 200:
                bizId = ""
                host_token = ""
                siteId = ""
                pageId = ""
                match = re.search("bizId%22%3A(.*?)%2C%22",text)
                if match:
                    bizId = match.group(1)
                match1 = re.search("host_token:'(.*?)'",text)
                if match1:
                    host_token = match1.group(1)
                match2 = re.search("siteId%22%3A(.*?)%2C%22",text)
                if match2:
                    siteId = match2.group(1)
                match3 = re.search("pageId%22%3A(.*?)%2C%22",text)
                if match3:
                    pageId = match3.group(1)
                language = "en_US"
                envMode = "product"
                renderType = "component"
                componentKeys = "companyCard"
                data = {"bizId": bizId, "language": language,"envMode":envMode,"hostToken":host_token,
                        "siteId":siteId,"pageId":pageId,"renderType":renderType,"componentKeys":componentKeys}
                meta = {"key":key}
                sale_url = "https://{}.alibaba.com/event/app/alisite/render.htm".format(key)
                if bizId and host_token and siteId and pageId:
                    yield scrapy.FormRequest(url=sale_url,callback=self.sale_money,formdata=data,meta=meta)
        else:
            try_result = self.try_again(response,key)
            yield try_result

    def sale_money(self, response):
        effective = '"success":true'
        meta = response.meta
        key = meta.get("key")
        if re.search(effective,response.text):
            companyName = ""
            ordAmt = ""
            ordCnt6m = ""
            company_type = ""
            companyJoinYears = ""
            match = re.search(r'\\"companyName\\":\\"(.*?)\\"',response.text)
            if match:
                companyName = match.group(1)
            match1 = re.search(r'\\"ordAmt\\":\\"(.*?)\\"',response.text)
            if match1:
                ordAmt = match1.group(1)
                ordAmt = ordAmt.replace(",","")
                ordAmt = ordAmt.replace("+","")
            match2 = re.search(r'\\"ordCnt6m\\":(\d*)',response.text)
            if match2:
                ordCnt6m = match2.group(1)
            match3 = re.search(r'\\"value\\":\\"(.*?)\\"', response.text)
            if match3:
                company_type = match3.group(1)
            match3 = re.search(r'\\"companyJoinYears\\":\\"(.*?)\\"', response.text)
            if match3:
                companyJoinYears = match3.group(1)
            item = GmWorkItem()
            item["key"] = key
            item["company_name"] = companyName
            item["sales_money"] = ordAmt
            item["sales_num"] = ordCnt6m
            item["company_type"] = company_type
            item["keep_time"] = companyJoinYears
            item["pipeline_level"] = "销量"
            yield item
        else:
            try_result = self.try_again(response, key)
            yield try_result

    def try_again(self,rsp,key):
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
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            item_e["key"] = key
            return item_e