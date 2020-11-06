# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class ZipCodeSpider(RedisSpider):
    name = 'zip_code'
    allowed_domains = ["yb21.cn"]
    start_urls = ['']
    redis_key = "zip_code:start_url"
    headers = headers_todict('''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: www.yb21.cn
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36''')
    error_key = "zip_code:error_key"


    def start_requests(self):
        url = "http://www.yb21.cn/"
        yield scrapy.Request(url=url, callback=self.parse, method="GET", headers=self.headers)

    def parse(self, response):
        youxiao = re.search('北京',response.text)
        if youxiao:
            urls = response.css(".citysearch").xpath("./ul/a/@href").getall()
            for i in urls:
                url = "http://www.yb21.cn"+i
                yield scrapy.Request(url=url,callback=self.parse1,method="GET",headers=self.headers)
        else:
            try_result = self.try_again(response)
            yield try_result

    def parse1(self,response):
        youxiao = re.search('post/code',response.text)
        if youxiao:
            urls = response.xpath("//table/tbody/tr/td/strong/a")
            for i in urls:
                id = i.xpath("./text()").get()
                url = i.xpath("./@href").get()
                url = "http://www.yb21.cn"+url
                yield scrapy.Request(url=url,callback=self.parse2,method="GET",headers=self.headers,meta={"id":id})
        else:
            try_result = self.try_again(response)
            yield try_result


    def parse2(self,response):
        id = response.meta.get("id")
        youxiao = re.search(id,response.text)
        if youxiao:
            postion = response.xpath("//table/tbody/tr[2]/td[2]")
            province = postion.xpath("./text()").get().encode("cp1252").decode("gbk")
            city = postion.xpath("./a[1]/text()").get().encode("cp1252").decode("gbk")
            area = postion.xpath("./a[2]/text()").get().encode("cp1252").decode("gbk")
            item = GmWorkItem()
            item["id"] = id
            item["province"] = province
            item["city"] = city
            item["area"] = area
            yield item
        else:
            try_result = self.try_again(response)
            yield try_result


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
