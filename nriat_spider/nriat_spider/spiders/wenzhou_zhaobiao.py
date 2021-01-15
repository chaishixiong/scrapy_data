# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class ZhaobiaoSpider(RedisSpider):
    name = 'zhaobiao'
    allowed_domains = ['wzzbtb.com']
    start_urls = ['https://ggzy.wzzbtb.com']
    redis_key = "zhaobiao:start_url"
    custom_settings = {"CONCURRENT_REQUESTS": 1,"DOWNLOAD_DELAY":1,"CHANGE_IP_NUM":20}
    error_key = "zhaobiao:error_url"

    def start_requests(self):
        url = "https://ggzy.wzzbtb.com/wzcms/zfcgzbgg/index.htm"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url, method="GET", headers=headers, meta={"first": True},dont_filter=True)

    def parse(self, response):
        youxiao = re.search("List-Li",response.text)
        first = response.meta.get("first")
        headers = self.get_headers(1)
        if youxiao:
            if first:
                page_str = response.css(".Zy-Page").xpath("./div/text()").get("")
                page = 0
                match = re.search("/(\d+)页",page_str)
                if match:
                    page = int(match.group(1))
                for i in range(2,page+1):
                    url = "https://ggzy.wzzbtb.com/wzcms/zfcgzbgg/index_{}.htm".format(i)
                    yield scrapy.Request(url=url, method="GET", headers=headers,dont_filter=True)
            list_li = response.css(".List-Li").xpath("./ul/li")
            for i in list_li:
                date = i.xpath("./span/text()").get()
                href = i.xpath("./a/@href").get()
                name = i.xpath("./a/@title").get()
                url = "https://ggzy.wzzbtb.com{}".format(href)
                yield scrapy.Request(url=url, method="GET",callback=self.data_parse, headers=headers,meta={"date":date,"name":name, "url": url})
        else:
            try_result = self.try_again(response)
            yield try_result

    def data_parse(self,response):
        jiaoyan = "BottomNone"
        meta = response.meta
        date = meta.get("date")
        name = meta.get("name")
        url = meta.get("url")
        if jiaoyan in response.text or "交易信息" in response.text:
            item_s = GmWorkItem()
            item_s["key"] = url
            item_s["source_code"] = response.text
            yield item_s
            laiyuan = re.findall('政采云',response.text)
            summaryPrice = ""
            winningSupplierName = ""
            try:
                if len(laiyuan) == 1:
                    trs = response.xpath('//table[contains(@class, "template-bookmark")]/tbody/tr')
                    if len(trs) == 1:
                        for tr in trs:
                            # 中标金额
                            summaryPrice = tr.xpath("./td[@class='code-summaryPrice']/text()").get()
                            summaryPrice = summaryPrice.split(':')[-1]
                            summaryPrice = summaryPrice.split('(')[0]
                            # 中标供应商名称
                            winningSupplierName = tr.xpath("./td[@class='code-winningSupplierName']/text()").get()
                    else:
                        summaryPrice = re.findall('报价:(\d+)\(元\)', response.text)[0]
                        winningSupplierName = re.findall('报价:(\d+)\(元\)</td><td width="10.0%" style="word-break:break-all;">(.*?)</td><td', response.text)[0][1]
                elif '项目预算' in response.text:
                    summaryPrice = response.xpath('//div[@align = "center"]/table/tbody/tr[2]/td[3]/div/font/text()').get()
                    winningSupplierName = response.xpath('//div[@align = "center"]/table/tbody/tr[2]/td[4]/div/font/text()').get()
                elif '预算金额' in response.text:
                    summaryPrice = response.xpath('//div[@align = "center"]/table/tbody/tr[2]/td[3]/div/font/text()').get()
                    winningSupplierName = response.xpath('//div[@align = "center"]/table/tbody/tr[2]/td[4]/div/font/text()').get()
                elif '￥' in response.text:
                    summaryPrice = re.findall('￥(.*?)元', response.text)[0]
                    winningSupplierName = re.findall('成交供应商：<strong><span style="text-decoration:underline;">(.*?)；</span></strong>', response.text)[0]
            except:
                summaryPrice = "error"
                winningSupplierName = "error"


            node = response.xpath('//span[contains(text(),"采购人名称") or contains(text(),"采购人信息") or contains(text(),"招标人名称")]')
            if not node:
                node = response.xpath('//font[contains(text(),"采购单位：") or contains(text(),"采购 单  位：")]')
            self_node = node.xpath("./text()").get("").strip()
            match = re.search("：(\w{3,})",self_node)
            if match:
                purchaser = match.group(1)
            else:
                purchaser = node.xpath("./parent::span/parent::strong/following-sibling::strong[1]/span/span/text()").get("").strip()
                if not purchaser:
                    purchaser = node.xpath("./parent::p/following-sibling::p[1]/span/span/text()").get("").strip()
                if not purchaser:
                    purchaser = node.xpath("./parent::strong/following-sibling::span[1]/text()").get("").strip()
                if not purchaser:
                    purchaser = node.xpath("./parent::strong/following-sibling::span[1]/span/text()").get("").strip()
            item = GmWorkItem()
            item["date"] = date
            item["name"] = name
            item["url"] = url
            item["summaryPrice"] = summaryPrice
            item["winningSupplierName"] = winningSupplierName
            item["purchaser"] = purchaser
            yield item
        else:
            try_result = self.try_again(response)
            yield try_result

    def try_again(self,rsp):
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
                self.server.lpush(self.error_key,data)
            except Exception as e:
                print(e)

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: ggzy.wzzbtb.com
Referer: https://ggzy.wzzbtb.com/wzcms/zfcgzbgg/index_3.htm
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
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
Host: m.ctrip.com'''
        return headers_todict(headers)
