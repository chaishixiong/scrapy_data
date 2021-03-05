# -*- coding: utf-8 -*-
import scrapy
import json
from nriat_spider.items import GmWorkItem
from tools.tools_request.header_tool import headers_todict
import re
from tools.tools_request.spider_class import RedisSpiderTryagain


class AlibabgjSpider(RedisSpiderTryagain):
    name = 'alibabagj_sort'
    allowed_domains = ['alibaba.com']
    start_urls = ['http://www.alibaba.com/']
    redis_key = "alibabagj_sort:start_url"
    custom_settings = {"REDIRECT_ENABLED":True,"CONCURRENT_REQUESTS":2,"CHANGE_IP_NUM":50}
    headers = headers_todict('''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36''')
    error_key = "alibabagj_sort:error_url"

    def start_requests(self):
        url = "https://www.alibaba.com/Products"
        yield scrapy.Request(url=url,method="GET",headers=self.headers)

    def parse(self, response):
        youxiao = re.search("(Categories)",response.text)
        if youxiao:
            text = response.text
            item_s = GmWorkItem()
            item_s["source_code"] = text
            yield item_s
            url_list = response.css(".sub-item-cont-wrapper").xpath("./ul/li/a")
            for i in url_list:
                url = i.xpath("./@href").get()
                url = self.process(url)
                name = i.xpath("./text()").get("").strip()
                yield scrapy.Request(url=url,callback=self.get_good,headers=self.headers,meta={"name":name,"first":True})
        else:
            try_result = self.try_again(response)
            yield try_result

    def get_good(self, response):
        effective = '(results for|ProductNormalList|m-gallery-product-item-wrap|not match any products)'
        meta = response.meta
        url = response.request.url
        name = meta.get("name")
        first = meta.get("first")
        if re.search(effective,response.text):
            text = response.text
            item_s = GmWorkItem()
            item_s["source_code"] = text
            if first:
                match = re.search('"offerTotalCount":(\d+)|"totalCount":(\d+)',response.text)
                if match:
                    total_count = match.group(1) if match.group(1) else match.group(2)
                    page_num = int(int(total_count)/48)+1 if int(total_count)%48 else int(int(total_count)/48)
                    page_num = min(page_num,100)
                    for i in range(2,page_num+1):
                        next_url = "{}?page={}".format(url,i)
                        yield scrapy.Request(url=next_url, callback=self.get_good, headers=self.headers,
                                             meta={"name": name})

            json_match = re.search("page__data__config = ({[\s\S]*?})\s+window.__page__data",response.text)
            if json_match:
                json_str = json_match.group(1)
                json_data = json.loads(json_str)
                props = json_data.get("props")
                offerResultData = props.get("offerResultData")
                offerList = offerResultData.get("offerList",[])
                for offer in offerList:
                    information = offer.get("information",{})
                    puretitle = information.get("puretitle")
                    productUrl = information.get("productUrl")
                    goods_id = information.get("id")
                    promotionInfoVO = offer.get("promotionInfoVO",{})
                    originalPriceFrom = promotionInfoVO.get("originalPriceFrom")
                    originalPriceTo = promotionInfoVO.get("originalPriceTo")
                    tradePrice = offer.get("tradePrice",{})
                    unit = tradePrice.get("unit")
                    minOrder = tradePrice.get("minOrder")
                    supplier = offer.get("supplier",{})
                    supplierYear = supplier.get("supplierYear")
                    supplierCountry = supplier.get("supplierCountry").get("name")
                    supplierProvince = supplier.get("supplierProvince").get("name")
                    supplierName = supplier.get("supplierName")
                    supplierHref = supplier.get("supplierHref")
                    supplierHref = supplierHref.replace(r"\/", "/")

                    supplierProductListHref = supplier.get("supplierProductListHref")
                    company = offer.get("company",{})
                    expCountry = company.get("expCountry")
                    record = company.get("record",{})
                    transaction = record.get("transaction",{})
                    conducted = transaction.get("conducted","")
                    conducted = conducted.replace(",","")
                    conducted = conducted.replace("+","")

                    num = transaction.get("num")
                    tradeAssurance = company.get("tradeAssurance")
                    transactionLevel = company.get("transactionLevelFloat")
                    responseRate = record.get("responseRate")
                    responseTime = record.get("responseTime")
                    reviews = offer.get("reviews",{})
                    reviewLink = reviews.get("reviewLink")
                    reviewScore = reviews.get("reviewScore")
                    reviewCount = reviews.get("reviewCount")
                    if goods_id:
                        item = GmWorkItem()
                        item["productUrl"] = productUrl
                        item["puretitle"] = puretitle
                        item["goods_id"] = goods_id
                        item["originalPriceFrom"] = originalPriceFrom
                        item["originalPriceTo"] = originalPriceTo
                    # item["unit"] = unit
                        item["minOrder"] = minOrder
                        item["supplierName"] = supplierName
                        item["supplierHref"] = supplierHref
                        item["expCountry"] = expCountry
                        item["reviewScore"] = reviewScore
                        item["reviewCount"] = reviewCount
                        item["pipeline_level"] = "goods"
                        yield item
                    match_s = "//(.*?)\.alibaba\.com|member/(.*?)/"
                    match = re.search(match_s, supplierHref)
                    if match:
                        supplierKey = match.group(1)
                    else:
                        supplierKey = ""
                    item_shop = GmWorkItem()
                    item_shop["supplierKey"] = supplierKey
                    item_shop["supplierName"] = supplierName
                    item_shop["supplierHref"] = supplierHref
                    item_shop["conducted"] = conducted
                    item_shop["num"] = num
                    item_shop["supplierYear"] = supplierYear
                    item_shop["expCountry"] = expCountry
                    item_shop["tradeAssurance"] = tradeAssurance
                    item_shop["transactionLevel"] = transactionLevel
                    item_shop["responseTime"] = responseTime
                    item_shop["responseRate"] = responseRate
                    item_shop["supplierCountry"] = supplierCountry
                    item_shop["supplierProvince"] = supplierProvince
                    item_shop["supplierProductListHref"] = supplierProductListHref
                    item_shop["reviewScore"] = reviewScore
                    item_shop["reviewCount"] = reviewCount
                    item_shop["reviewLink"] = reviewLink
                    item_shop["pipeline_level"] = "goods"
                    yield item_shop
        else:
            try_result = self.try_again(response)
            yield try_result

    def process(self,str_input):
        str_input = str_input.replace("http:", "https:")
        str_input = str_input.replace("-/-", "-")
        if "catalog" not in str_input:
            str_input = str_input.replace("com/", "com/catalog/")
        str_input = str_input.replace("pid", "cid")
        str_input = re.sub(r"([^g])/(\w{4,6}-)", r"\1-\2", str_input)
        return str_input