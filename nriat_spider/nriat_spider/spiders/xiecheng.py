# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re,json


class XiechengSpider(RedisSpider):
    name = 'xiecheng'
    allowed_domains = ['ctrip.com']
    start_urls = ['https://www.ctrip.com/']
    redis_key = "xiecheng:start_url"
    custom_settings = {"CONCURRENT_REQUESTS":2,"DOWNLOADER_MIDDLEWARES":{'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 20,
                       'nriat_spider.middlewares.UpdatetimeMiddleware': 23,'nriat_spider.middlewares.IpChangeDownloaderMiddleware': 21,}}


    def start_requests(self):
        url = "https://hotels.ctrip.com/Domestic/Tool/AjaxGetCitySuggestion.aspx"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",headers=headers)


    def parse(self, response):
        youxiao = re.search("suggestion=(\{.*\})",response.text)
        url_key = response.request.url
        if youxiao and "北京" in response.text:
            json_str = youxiao.group(1)
            data_list = re.findall("(\{display.*?\})",json_str)
            city_set = set()
            for i in data_list:
                match = re.search('data:"(.*?)"',i)
                if match:
                    data = match.group(1)
                    data_info = data.split("|")
                    if len(data_info) ==3:
                        pinyin = data_info[0]
                        name = data_info[1]
                        city_id = data_info[2]
                        if name not in city_set:
                            url = "https://m.ctrip.com/restapi/soa2/16709/HotelSearch"
                            page = "1"
                            home_url = "https://hotels.ctrip.com/hotels/listPage?cityename={}&city={}".format(pinyin,city_id)
                            headers = self.get_headers(2)
                            headers["Referer"] = home_url
                            data = '''{"meta":{"fgt":"","hotelId":"","priceToleranceData":"","priceToleranceDataValidationCode":"","mpRoom":[],"hotelUniqueKey":"","shoppingid":""},"seqid":"","deduplication":[],"filterCondition":{"star":[],"rate":"","rateCount":[],"priceRange":{"lowPrice":0,"highPrice":-1},"priceType":"","breakfast":[],"payType":[],"bedType":[],"bookPolicy":[],"bookable":[],"discount":[],"zone":[],"landmark":[],"metro":[],"airportTrainstation":[],"location":[],"cityId":[],"amenty":[],"promotion":[],"category":[],"feature":[],"brand":[],"popularFilters":[]},"searchCondition":{"sortType":"1","adult":1,"child":0,"age":"","pageNo":页数,"optionType":"","optionId":"","lat":0,"destination":"","keyword":"","cityName":"城市名称","lng":0,"cityId":城市id,"checkIn":"入住时间","checkOut":"离店时间","roomNum":1,"mapType":"gd","travelPurpose":0,"countryId":1,"url":"酒店url","pageSize":20,"timeOffset":28800,"radius":0,"directSearch":0},"queryTag":"NORMAL","genk":true,"genKeyParam":"a=0,b=入住时间,c=离店时间,d=zh-cn,e=2","webpSupport":true,"platform":"online","pageID":"102002","head":{"Version":"","userRegion":"CN","Locale":"zh-CN","LocaleController":"zh-CN","TimeZone":"8","Currency":"CNY","PageId":"102002","webpSupport":true,"userIP":"","P":"","ticket":"","clientID":"","Union":{"AllianceID":"","SID":"","Ouid":""},"HotelExtension":{"group":"CTRIP","hasAidInUrl":false,"Qid":"","hotelUuidKey":"","hotelUuid":""}}}'''
                            data = data.replace("页数", page)
                            data = data.replace("城市名称", name)
                            data = data.replace("城市id", city_id)
                            data = data.replace("酒店url", home_url)
                            meta = {"pinyin": pinyin, "name": name, "city_id": city_id, "page": page}
                            yield scrapy.Request(url=url, callback=self.data_parse, method="POST", body=data,
                                                 headers=headers, meta=meta)
                            city_set.add(name)
        else:
            try_result = self.try_again(response,url=url_key)
            yield try_result
    def data_parse(self,response):
        jiaoyan = "Success"
        meta = response.meta
        pinyin = meta.get("pinyin")
        name = meta.get("name")
        city_id = meta.get("city_id")
        page = meta.get("page")

        if jiaoyan in response.text:
            data_json = json.loads(response.text)
            Response = data_json.get("Response")
            resultTitle = Response.get("resultTitle")
            hotel_num = re.sub("\D","",resultTitle)
            #添加剩余页面
            if page == "1" and hotel_num:
                totle_num = int(int(hotel_num)/20)+1 if int(hotel_num)%20 else int(int(hotel_num)/20)

                # if totle_num>2:#test
                #     totle_num = 2

                headers = self.get_headers(2)
                home_url = "https://hotels.ctrip.com/hotels/listPage?cityename={}&city={}".format(pinyin, city_id)
                url = "https://m.ctrip.com/restapi/soa2/16709/HotelSearch"
                headers["Referer"] = home_url
                for i in range(2,totle_num+1):
                    data = '''{"meta":{"fgt":"","hotelId":"","priceToleranceData":"","priceToleranceDataValidationCode":"","mpRoom":[],"hotelUniqueKey":"","shoppingid":""},"seqid":"","deduplication":[],"filterCondition":{"star":[],"rate":"","rateCount":[],"priceRange":{"lowPrice":0,"highPrice":-1},"priceType":"","breakfast":[],"payType":[],"bedType":[],"bookPolicy":[],"bookable":[],"discount":[],"zone":[],"landmark":[],"metro":[],"airportTrainstation":[],"location":[],"cityId":[],"amenty":[],"promotion":[],"category":[],"feature":[],"brand":[],"popularFilters":[]},"searchCondition":{"sortType":"1","adult":1,"child":0,"age":"","pageNo":页数,"optionType":"","optionId":"","lat":0,"destination":"","keyword":"","cityName":"城市名称","lng":0,"cityId":城市id,"checkIn":"入住时间","checkOut":"离店时间","roomNum":1,"mapType":"gd","travelPurpose":0,"countryId":1,"url":"酒店url","pageSize":20,"timeOffset":28800,"radius":0,"directSearch":0},"queryTag":"NORMAL","genk":true,"genKeyParam":"a=0,b=入住时间,c=离店时间,d=zh-cn,e=2","webpSupport":true,"platform":"online","pageID":"102002","head":{"Version":"","userRegion":"CN","Locale":"zh-CN","LocaleController":"zh-CN","TimeZone":"8","Currency":"CNY","PageId":"102002","webpSupport":true,"userIP":"","P":"","ticket":"","clientID":"","Union":{"AllianceID":"","SID":"","Ouid":""},"HotelExtension":{"group":"CTRIP","hasAidInUrl":false,"Qid":"","hotelUuidKey":"","hotelUuid":""}}}'''
                    data = data.replace("页数", str(i))
                    data = data.replace("城市名称", name)
                    data = data.replace("城市id", city_id)
                    data = data.replace("酒店url", home_url)
                    meta = {"pinyin": pinyin, "name": name, "city_id": city_id, "page": str(i)}
                    yield scrapy.Request(url=url, callback=self.data_parse, method="POST", body=data, headers=headers, meta=meta)

            hotelList = Response.get("hotelList",dict())
            list_data = hotelList.get("list",[])
            for i in list_data:
                base = i.get("base")
                hotelId = base.get("hotelId")
                hotelEnName = base.get("hotelEnName")
                hotelName =base.get("hotelName")
                tags = str(base.get("tags",""))
                comment = i.get("comment")
                content = comment.get("content","")
                comment_num = re.sub("\D","",content)
                money = i.get("money")
                price = money.get("price")
                position = i.get("position")
                cityName = position.get("cityName")
                area = position.get("area")
                address = position.get("address")
                score = i.get("score")
                number = score.get("number")
                item = GmWorkItem()
                item["hotel_num"] = hotel_num
                item["hotel_id"] = hotelId
                item["hotel_name"] = hotelName
                item["hotel_enname"] = hotelEnName
                item["tag"] = tags
                item["price"] = price
                item["city"] = cityName
                item["area"] = area
                item["address"] = address
                item["comment_num"] = comment_num
                item["comment"] = number
                yield item
        else:
            try_result = self.try_again(response,pinyin=pinyin,name=name,id=city_id,page=page)
            yield try_result

    def try_again(self,rsp,**kwargs):
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
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Host: hotels.ctrip.com
Pragma: no-cache
Referer: https://www.ctrip.com/
Sec-Fetch-Mode: no-cors
Sec-Fetch-Site: same-site
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
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
