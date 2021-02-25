# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
from urllib import parse
from twisted.web.http_headers import Headers as TwistedHeaders
from tools.tools_request.spider_class import RedisSpiderTryagain


TwistedHeaders._caseMappings.update({
    b'Host': b'host',
    b'User-Agent': b'user-agent',
    b'accept-encoding': b'accept-encoding',
    b'accept': b'accept',
    b'Connection': b'connection',
    b'accept-language': b'accept-language',
    b'upgrade-insecure-requests': b'upgrade-insecure-requests'
})

class AmazonSortShop(RedisSpiderTryagain):
    name = 'amazonuk_sort_shop'
    allowed_domains = ['amazon.co.uk']
    start_urls = ['http://www.amazon.co.uk/']
    redis_key = "amazonuk_sort_shop:start_url"
    error_key = "amazonuk_sort_shop:error_url"
    custom_settings = {"CONCURRENT_REQUESTS":2,"DOWNLOADER_MIDDLEWARES":{'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,
                                                                    'nriat_spider.middlewares.UserAgentChangeDownloaderMiddleware':20
}}
    headers = '''Host: www.amazon.co.uk
User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36
accept-encoding: gzip, deflate, br
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Connection: keep-alive
accept-language: zh-CN,zh;q=0.9
upgrade-insecure-requests: 1'''
    def make_requests_from_url(self, seed):
        # data = seed.split(",")
        url = seed.strip()
        url = parse.unquote(url)
        # sort = data[1]
        return scrapy.Request(url=url, method="GET", headers=headers_todict(self.headers),dont_filter=True)

    def parse(self, response):
        url = response.url
        youxiao = re.search("(search-alias)",response.text)
        if youxiao:
            sort_match = re.search(r'<option.+?current="parent" value="search-alias=.+?>(.+?)</option>', response.text)
            if sort_match:
                sort = sort_match.group(1)
            else:
                sort = ""
            seller_id = re.findall(r'Cp_6%3A(\w+)">|Cp_6%3A(\w+)&amp', response.text)
            for i in seller_id:
                if i[0]:
                    shop_id = i[0]
                else:
                    shop_id = i[1]
                item = GmWorkItem()
                item["key"] = url
                item["shop_id"] = shop_id
                item["sort"] = sort
                yield item
        else:
            try_result = self.try_again(response)
            yield try_result
