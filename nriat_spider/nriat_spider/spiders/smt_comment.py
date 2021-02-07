# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import time
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat


class SmtCommentSpider(RedisSpider):
    name = 'smt_comment'
    allowed_domains = ['aliexpress.com']
    start_urls = ['https://www.aliexpress.com']
    redis_key = "smt_comment:start_url"
    error_key = "smt_comment:error_url"
    custom_settings={
        "CHANGE_IP_NUM":200,"CONCURRENT_REQUESTS":6
    }

    current_mouth = time.localtime(time.time()).tm_mon#这里获取当前的月份
    mouth_dict1 = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
    "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12 }
    mouth_dict = { x.upper():y for x,y in mouth_dict1.items()}
    # print(mouth_dict)

    def make_requests_from_url(self, url):
    #     url = "http://www.baidu.com"
    #     yield scrapy.Request(url, callback=self.seed_request,dont_filter=True, method="GET")
    #
    # def seed_request(self,response):
        page = ""
        currentPage = "1"
        data = url.strip().split(",")
        ownerMemberId = data[0]#seller_id
        productId = data[1]
        request = self.request(ownerMemberId,productId,page,currentPage)
        return request

    def request(self,ownerMemberId,productId,page,currentPage):
        url = "https://feedback.aliexpress.com/display/productEvaluation.htm"
        referer = "https://feedback.aliexpress.com/display/productEvaluation.htm?v=2&productId={}&ownerMemberId={}&memberType=seller&startValidDate=&i18n=true"
        headers = self.get_headers("1")
        data = self.get_data()
        referer = referer.format(productId,ownerMemberId)
        headers["referer"] = referer
        meta={"ownerMemberId" :ownerMemberId,
        "productId" : productId,
        "page" : page
        }
        data["ownerMemberId"] = ownerMemberId
        data["productId"] = productId
        data["page"] = page
        data["currentPage"] = currentPage
        return scrapy.FormRequest(url,headers=headers,formdata=data, method="POST",meta=meta)

    def parse(self, response):
        youxiao = re.search("feedback-container|feedbackServer",response.text)
        meta = response.meta
        seller_id = meta.get("ownerMemberId")
        goods_id = meta.get("productId")
        page = meta.get("page")
        if not page:
            page = "1"
        if youxiao:
            item_s = GmWorkItem()
            item_s["key"] = goods_id
            item_s["source_code"] = response.text
            yield item_s
            comment_num_str = response.css(".fb-star-selector").xpath("./em/text()").get()
            comment_num = 0
            if comment_num_str:
                match = re.search("(\d+)",comment_num_str)
                if match:
                    comment_num = match.group(1)
            rate_list = response.css(".rate-list").xpath("./li")
            rate = []
            for i in rate_list:
                comment_score_1 = i.xpath("./span[3]/text()").get()
                rate.append(comment_score_1)
            comment_distribution = str(rate)
            feedbacks = response.css(".feedback-list-wrap").xpath("./div")
            mouth = ""
            day_match = ""
            for i in feedbacks:
                user_name = i.css(".user-name").xpath("./a/text()").get()
                if not user_name:
                    user_name = i.css(".user-name").xpath("./text()").get()
                country = i.css(".user-country").xpath("./b/text()").get()
                comment_score = i.css(".star-view").xpath("./span/@style").get()
                # user_info = i.css(".user-order-info")
                # colour = user_info.xpath("./span[1]/text()").get()
                # Logistics = user_info.xpath("./span[2]/text()").get()
                buyer_feedback = i.css(".buyer-feedback")
                comment = buyer_feedback.xpath("./span[1]/text()").get()
                time = buyer_feedback.xpath("./span[2]/text()").get()
                item = GmWorkItem()
                item["seller_id"] = seller_id
                item["goods_id"] = goods_id
                item["current_page"] = page
                item["comment_num"] = comment_num
                item["comment_distribution"] = comment_distribution
                item["user_name"] = user_name
                item["country"] = country
                item["comment_score"] = comment_score
                item["comment"] = comment
                item["time"] = time
                #seller_id,goods_id,current_page,comment_num,comment_distribution,user_name,country,comment_score,comment,time
                yield item
                if time:
                    mouth_match = re.search("\d+ ([a-z]+) \d{4}",time,flags=re.I)
                    if mouth_match:
                        mouth = mouth_match.group(1)
                    day_match = re.search("(\d+) [a-z]+ \d{4}",time,flags=re.I)
                    if day_match:
                        day_match = day_match.group(1)

            page_mouth = self.mouth_dict.get(mouth.upper())

            if (page_mouth == self.current_mouth or page_mouth == self.current_mouth-1) and int(page)*10<int(comment_num):#这里跨年问题or page_mouth in [1,12,11,10,9]
                ownerMemberId = seller_id
                productId = goods_id
                page = int(page)+1
                current_page = page-1
                request = self.request(ownerMemberId, productId, str(page), str(current_page))
                yield request
        else:
            try_result = self.try_again(response, seller_id=seller_id,goods_id=goods_id,current_page=page)
            yield try_result


    def try_again(self,rsp,**kwargs):
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
            # item_e = GmWorkItem()
            # item_e["error_id"] = 1
            # for i in kwargs:
            #     item_e[i] = kwargs[i]
            # return item_e

    def get_headers(self,type="1"):
        if type == "1":
            headers = '''Host: feedback.aliexpress.com
            Connection: keep-alive
            Cache-Control: max-age=0
            Origin: https://feedback.aliexpress.com
            Upgrade-Insecure-Requests: 1
            Content-Type: application/x-www-form-urlencoded
            User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
            Referer: https://feedback.aliexpress.com/display/productEvaluation.htm?v=2&productId=32996635572&ownerMemberId=230443220&memberType=seller&startValidDate=&i18n=true
            Accept-Encoding: gzip, deflate, br
            Accept-Language: zh-CN,zh;q=0.9'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)

    def get_data(self):
        form_data = {
            "ownerMemberId": "230443220",
            "memberType": "seller",
            "productId": "32996635572",
            "companyId": "",
            "evaStarFilterValue": "allStars",
            "evaSortValue": "sortlarest@feedback",
            "page": "2",
            "currentPage": "1",
            "startValidDate": "",
            "i18n": "true",
            "withPictures": "false",
            "withPersonalInfo": "false",
            "withAdditionalFeedback": "false",
            "onlyFromMyCountry": "false",
            "version": "",
            "isOpened": "true",
            "translate": "Y",
            "jumpToTop": "true",
            "v": "2"
        }
        return form_data
