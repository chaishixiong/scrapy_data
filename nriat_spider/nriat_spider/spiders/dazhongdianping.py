# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
import jsonpath,json



class DianPingSpider(RedisSpider):
    name = 'dianping'
    allowed_domains = ['dianping.com']
    start_urls = ['https://m.dianping.com/']
    redis_key = "dianping:start_url"
    custom_settings = {"DOWNLOAD_DELAY":2,"CHANGE_IP_NUM":10,"DOWNLOADER_MIDDLEWARES" : {'nriat_spider.middlewares.DaZhongDianPingDownloaderMiddleware': 20,
        'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,},}
    # Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password="nriat.123456", max_connections=3)
    # server = redis.Redis(host='192.168.0.226', port=5208, decode_responses=True)
    error_key = "dianping:error_url"
    cate_list =[[10,"美食"],[25,"电影演出赛事"],[30,"休闲娱乐"],[60,"酒店"],[50,"丽人"],[15,"K歌"],[45,"运动健身"],[35,"周边游"],[70,"亲子"],[55,"结婚"],[20,"购物"],[95,"宠物"],[80,"生活服务"],[75,"学习培训"],[65,"爱车"],[85,"医疗健康"],[90,"家居"],[40,"宴会"]]
    limit_num = 2000
    zhejiang_city_name = ["安吉县","苍南","长兴县","常山县","淳安县","慈溪","岱山县","德清县","东阳","洞头区","奉化","富春江","富阳区","海宁市","海盐县","杭州","横店","湖州","嘉善县","嘉兴","建德市","江山市","金华","缙云县","景宁畲族自治县","开化县","柯桥区","兰溪市","丽水","临安","临海市","龙港市","龙泉市","龙游县","莫干山","宁波","宁海","磐安县","平湖市","平阳","浦江县","普陀山","千岛湖","青田县","庆元县","衢州","瑞安","三门县","上虞区","绍兴","嵊泗县","嵊州市","松阳县","遂昌县","台州","泰顺县","天目山","天台县","桐庐县","桐乡市","温岭市","温州","文成县","乌镇","武义县","西塘","仙都","仙居县","象山","新昌县","乐清","雁荡山","义乌","永嘉县","永康","余姚","玉环市","云和县","镇海区","舟山","朱家尖","诸暨"]
    quzhou_city = ["江山市","常山县","开化县","龙游县","衢州"]

    def start_requests(self):
        url = "http://www.dianping.com/citylist"
        headers =self.get_headers(2)
        yield scrapy.Request(url=url, callback=self.get_city, method="GET",headers=headers,dont_filter=True)

    def get_city(self, response):
        req_success = "北京"
        if req_success:
            headers = self.get_headers(2)
            lis = response.xpath('//ul/li//a')
            for li in lis:
                url = li.xpath("./@href").get("")
                name = li.xpath("./text()").get()
                if url and name in self.quzhou_city:
                    url = 'https:' + url
                    yield scrapy.Request(url=url, callback=self.get_cate, method="GET",headers=headers,meta={"city":name})

    def get_cate(self,response):
        req_success = "'cityId'"
        city_name = response.meta.get("city")
        if req_success:
            headers = self.get_headers(1)
            # headers["Cookie"] = "cityid=3; _hc.v=6486a1f6-19a6-d5bc-dfd9-bac008f8bafa.1590568859; msource=default; default_ab=shopList%3AC%3A5; _lxsdk_s=172554ab5d4-cc7-89c-1f7%7C%7C1; logan_session_token=sl63sc5x5e9fe3u4qfam; logan_custom_report="
            match = re.search("'cityId': ?'(\d+)'",response.text)
            if match:
                url = "https://m.dianping.com/isoapi/module"
                city_id = match.group(1)
                for i in self.cate_list:
                    cate_id = i[0]
                    cate_name = i[1]
                    start = "0"
                    categoryId = cate_id
                    parentCategoryId = cate_id
                    headers["Referer"] = "https://m.dianping.com/quzhou/ch{}".format(cate_id)
                    meta = {"city_name":city_name,"city_id":city_id,"cate_id":cate_id,"cate_name":cate_name,"first":True}
                    data = '''{"pageEnName":"shopList","moduleInfoList":[{"moduleName":"mapiSearch","query":{"search":{"start":%s,"categoryId":"%s","parentCategoryId":%s,"locateCityid":0,"limit":20,"sortId":"0","cityId":%s,"range":-1,"maptype":0,"keyword":""}}}]}''' %(start,categoryId,parentCategoryId,city_id)
                    yield scrapy.Request(url=url, callback=self.get_detail, method="POST", body=data,headers=headers,meta=meta)

    def get_detail(self, response):
        meta = response.meta
        city_name = meta.get("city_name")
        city_id = meta.get("city_id")
        cate_id = meta.get("cate_id")
        cate_name = meta.get("cate_name")
        first = meta.get("first")

        youxiao = re.search('("success")', response.text)
        if youxiao:
            item_s = GmWorkItem()
            item_s["source_code"] = response.text
            yield item_s
            headers = self.get_headers(1)
            # headers["Cookie"] = "cityid=3; _hc.v=6486a1f6-19a6-d5bc-dfd9-bac008f8bafa.1590568859; msource=default; default_ab=shopList%3AC%3A5; _lxsdk_s=172554ab5d4-cc7-89c-1f7%7C%7C1; logan_session_token=sl63sc5x5e9fe3u4qfam; logan_custom_report="
            json_data = json.loads(response.text)
            listData = jsonpath.jsonpath(json_data,"$..listData")
            if listData:
                list = listData[0].get("list")
                recordCount = listData[0].get("recordCount")
                if first:
                    url = "https://m.dianping.com/isoapi/module"
                    meta_next = {"city_name": city_name, "city_id": city_id, "cate_id": cate_id, "cate_name": cate_name}
                    city_shopnum = recordCount
                    if city_shopnum>self.limit_num:
                        city_shopnum = self.limit_num
                    for i in range(20,city_shopnum+1,20):
                        categoryId = cate_id
                        parentCategoryId = cate_id
                        cityId = city_id
                        data = '''{"pageEnName":"shopList","moduleInfoList":[{"moduleName":"mapiSearch","query":{"search":{"start":%s,"categoryId":"%s","parentCategoryId":%s,"locateCityid":0,"limit":20,"sortId":"0","cityId":%s,"range":-1,"maptype":0,"keyword":""}}}]}''' % \
                               (i, categoryId, parentCategoryId, cityId)
                        yield scrapy.Request(url=url, callback=self.get_detail, method="POST", body=data, headers=headers,meta=meta_next)
                for i in list:
                    shop_id = i.get("shopuuid")
                    shop_name = i.get("name")
                    branchName = i.get("branchName")
                    starScore = i.get("starScore")
                    reviewCount = i.get("reviewCount")
                    priceText = i.get("priceText")
                    regionName = i.get("regionName")
                    categoryName = i.get("categoryName")
                    dishtags = i.get("dishtags")
                    hasTakeaway = i.get("hasTakeaway")
                    item = GmWorkItem()
                    item["city_shopnum"] = recordCount
                    item["shop_id"] = shop_id
                    item["shop_name"] = shop_name
                    item["branch_name"] = branchName
                    item["star_score"] = starScore
                    item["review_count"] = reviewCount
                    item["price_text"] = priceText
                    item["region_name"] = regionName
                    item["category_name"] = categoryName
                    item["dish_tags"] = dishtags
                    item["has_takeaway"] = hasTakeaway
                    item["city_name"] = city_name
                    item["cate_name"] = cate_name
                    yield item
        else:
            try_result = self.try_again(response)
            if try_result:
                yield try_result

    def try_again(self, rsp, **kwargs):
        max_num = 3
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
            # item_e = GmWorkItem()
            # item_e["error_id"] = 1
            # for i in kwargs:
            #     item_e[i] = kwargs[i]
            # return item_e

    def get_headers(self, type=1):
        if type == 1:
            headers = '''Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Content-Type: application/json
Host: m.dianping.com
Origin: https://m.dianping.com
Pragma: no-cache
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        else:
            headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Host: www.dianping.com
Pragma: no-cache
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        return headers_todict(headers)
