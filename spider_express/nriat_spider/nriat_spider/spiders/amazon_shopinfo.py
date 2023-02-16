# -*- coding: utf-8 -*-
import scrapy
from tools.tools_request.spider_class import RedisSpiderTryagain
from nriat_spider.items import AmazonItem
from tools.tools_request.header_tool import headers_todict
import re
from lxml import etree
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
        url = "https://www.amazon.com/sp?ie=UTF8&isCBA=&language=en_ZH&seller={}&tab=&vasStoreID=".format(id)
        headers = headers_todict(self.headers)
        headers['cookie'] = 'session-id=137-0489966-7453666; i18n-prefs=USD; ubid-main=132-2961476-4810337; session-id-jp=355-9057861-4050835; ubid-acbjp=357-3763949-7715242; s_pers=%20s_fid%3D227B8ED09C84DAE8-27437224EA0E76B0%7C1807154523899%3B%20s_dl%3D1%7C1649389923899%3B%20gpv_page%3DSC%253AJP%253AWP-Welcome%7C1649389923900%3B%20s_ev15%3D%255B%255B%2527SCJPWPDirect%2527%252C%25271649388123902%2527%255D%255D%7C1807154523902%3B; _msuuid_jniwozxj70=51330998-3131-4986-A668-C134D7FD8B2B; s_nr=1666168416409-Repeat; s_vnum=2098149743861%26vn%3D2; s_dslv=1666168416410; av-timezone=Asia/Shanghai; session-id-time=2082787201l; sp-cdn="L5Z9:CN"; lc-main=en_US; session-token="osO6lpKS4RmVZB74eSqb7/rXmn7l372CshKYd/xcWqRO14fP+/XLYnVaUFvnD4A0ShJtZrc28TJFsyCwgRo7U/rV2czZmsCguSu02PSXTa28JJN4STFavcV82sZSxsoxDPrYmitRgz3/0qFWn6atnRu9XJ9kcGuRXY8kz6IkGjceMLRjmESCbNKADnSEfcLjWs0Svfrqs+O+xASbFE5bQi+9JiFV1rqpbPZIxbJC9vY="; csm-hit=tb:F00YHYB0KZMZ5D91TBHE+s-F00YHYB0KZMZ5D91TBHE|1667808086135&t:1667808086135&adb:adblk_no'
        return scrapy.Request(url=url, method="GET", headers=headers, meta={"id":id,"proxy":"127.0.0.1:8080"})#

    def parse(self, response):
        youxiao = re.search("(Detailed Seller|errors/404)",response.text)
        id = response.meta.get("id")
        if youxiao:
            shop_id = id
            text_html = etree.HTML(response.text)
            text = response.text
            shop_name = ""
            shop_info = ""
            company = ""
            country = ""
            postcode = ""
            shop_name_match = re.search('sellerName-rd">([^<]*)</h1>',text)
            if shop_name_match:
                shop_name = shop_name_match.group(1)
            shop_info_match = re.search('"a-row a-spacing-none spp-expander-more-content">([^/]*)</div>',text)
            if shop_info_match:
                shop_info = shop_info_match.group(1)
            company_match = re.search('</span><span>([^<]*)</span></div><div class="a-row a-spacing-none"><span class="a-text-bold">',text)
            if company_match:
                company = company_match.group(1)
            company_address = text_html.xpath('//div[@id="page-section-detail-seller-info"]/div/div/div//div[4]/span/text()')[0]
            country_match = re.search('<span>(CN)</span></div>',text)
            if country_match:
                country = country_match.group(1)
            postcode = ''
            html_list = text_html.xpath('//div[@class="a-row a-spacing-none indent-left"]/span/text()')
            html = ''
            if len(html_list) > 1:
                for i in html_list:
                    p = re.match(r"\d+$", i)
                    html += i
                    if p != None:
                        postcode = str(i)
            goodrate_mouth = text_html.xpath('//span[@id="effective-timeperiod-rating-thirty-description"]/text()')
            # middlerate_mouth = response.css("#feedback-summary-table").xpath("./tr[3]/td[2]").xpath("string(.)").get("").strip()
            # badrate_mouth = response.css("#feedback-summary-table").xpath("./tr[4]/td[2]").xpath("string(.)").get("").strip()
            # comment_mouth = response.css("#feedback-summary-table").xpath("./tr[5]/td[2]").xpath("string(.)").get("").strip()
            comment_mouth = text_html.xpath('//div[@id="rating-thirty-num"]/span[1]/text()')

            goodrate_quarterly = text_html.xpath('//span[@id="effective-timeperiod-rating-ninety-description"]/text()')
            # middlerate_quarterly = response.css("#feedback-summary-table").xpath("./tr[3]/td[3]").xpath("string(.)").get("").strip()
            # badrate_quarterly = response.css("#feedback-summary-table").xpath("./tr[4]/td[3]").xpath("string(.)").get("").strip()
            # comment_quarterly = response.css("#feedback-summary-table").xpath("./tr[5]/td[3]").xpath("string(.)").get("").strip()
            comment_quarterly = text_html.xpath('//div[@id="rating-90-num"]/span[1]/text()')

            goodrate_year = text_html.xpath('//span[@id="effective-timeperiod-rating-year-description"]/text()')
            # middlerate_year = response.css("#feedback-summary-table").xpath("./tr[3]/td[4]").xpath("string(.)").get("").strip()
            # badrate_year = response.css("#feedback-summary-table").xpath("./tr[4]/td[4]").xpath("string(.)").get("").strip()
            # comment_year = response.css("#feedback-summary-table").xpath("./tr[5]/td[4]").xpath("string(.)").get("").strip()
            comment_year = text_html.xpath('//div[@id="rating-365d-num"]/span[1]/text()')

            goodrate_total = text_html.xpath('//span[@id="effective-timeperiod-rating-lifetime-description"]/text()')
            # middlerate_total = response.css("#feedback-summary-table").xpath("./tr[3]/td[5]").xpath("string(.)").get("").strip()
            # badrate_total = response.css("#feedback-summary-table").xpath("./tr[4]/td[5]").xpath("string(.)").get("").strip()
            # comment_total = response.css("#feedback-summary-table").xpath("./tr[5]/td[5]").xpath("string(.)").get("").strip()
            comment_total = text_html.xpath('//div[@id="rating-lifetime-num"]/span[1]/text()')
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
            # item["middlerate_mouth_info"] = middlerate_mouth
            # item["badrate_mouth_info"] = badrate_mouth
            item["comment_mouth_info"] = comment_mouth
            item["goodrate_quarterly"] = goodrate_quarterly
            # item["middlerate_quarterly"] = middlerate_quarterly
            # item["badrate_quarterly"] = badrate_quarterly
            item["comment_quarterly"] = comment_quarterly
            item["goodrate_year"] = goodrate_year
            # item["middlerate_year"] = middlerate_year
            # item["badrate_year"] = badrate_year
            item["comment_year"] = comment_year
            item["goodrate_total"] = goodrate_total
            # item["middlerate_total"] = middlerate_total
            # item["badrate_total"] = badrate_total
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
