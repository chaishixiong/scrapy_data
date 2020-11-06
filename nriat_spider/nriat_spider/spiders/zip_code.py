# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class ZipCode1Spider(RedisSpider):
    name = 'zip_code1'
    allowed_domains = [""]
    start_urls = ['']
    redis_key = "zip_code1:start_url"
    headers = headers_todict('''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: www.youbianku.com
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36''')
    error_key = "zip_code1:error_key"
    custom_settings = {"DOWNLOAD_DELAY":0.1,"CONCURRENT_REQUESTS":2,"CHANGE_IP_NUM":50}


    def make_requests_from_url(self, url):
        id = url.strip()
        url = "https://www.youbianku.com/{}".format(id)
        return scrapy.Request(url=url, callback=self.parse, method="GET", headers=self.headers,meta={"id":id})

    def parse(self, response):
        id = response.meta.get("id")
        youxiao = re.search('breadcrumb|邮政编码',response.text)
        if youxiao:
            infomation = response.css(".breadcrumb")
            province = infomation.xpath("./span[2]/a/span/text()").get("")
            city = infomation.xpath("./span[3]/a/span/text()").get("")
            area = infomation.xpath("./span[4]/a/span/text()").get("")
            area = area.replace(province,"")
            area = area.replace(city,"")
            item = GmWorkItem()
            item["id"]=id
            item["province"]=province
            item["city"]=city
            item["area"]=area
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