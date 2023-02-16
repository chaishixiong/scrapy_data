import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
from urllib import parse
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

class AmazonUkSortShopSpider(RedisSpider):
    name = 'amazon_uk_sort_shop'
    allowed_domains = ['amazon.co.uk']
    start_urls = ['http://www.amazon.co.uk/']
    redis_key = "amazon_uk_sort_shop:start_url"
    error_key = "amazon_uk_sort_shop:error_url"
    custom_settings = {"DOWNLOAD_DELAY":1,"DOWNLOADER_MIDDLEWARES":{'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,
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
        url = 'https://www.amazon.co.uk/dp/{}'.format(seed)
        # url = 'https://www.amazon.co.uk/dp/1562054686'
        return scrapy.Request(url=url, method="GET", headers=headers_todict(self.headers), meta={"sort": seed}, dont_filter=True)

    def parse(self, response):
        youxiao = re.search(r'seller=(.*?)(">|&amp)', response.text)
        goods_id = response.meta.get("sort")
        if youxiao != None:
            print("成功")
            item = GmWorkItem()
            item["goods_id"] = goods_id
            item["shop_id"] = youxiao.group(1)
            yield item
        else:
            try_result = self.try_again(response)
            yield try_result

    def try_again(self, rsp):
        max_num = 5
        meta = rsp.meta
        try_num = meta.get("try_num", 0)
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
