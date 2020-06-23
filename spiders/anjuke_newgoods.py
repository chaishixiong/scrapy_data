# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from nriat_spider.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re


class AnjukeNewgoodsSpider(RedisSpider):
    name = 'anjuke_newgoods'
    allowed_domains = ['anjuke.com']
    start_urls = ['https://m.anjuke.com']
    redis_key = "anjuke_newgoods:start_url"
    custom_settings = {"CONCURRENT_REQUESTS":4,"CHANGE_IP_NUM":50,"SCHEDULER_QUEUE_CLASS": 'scrapy_redis.queue.FifoQueue'}
    file_name = r"W:\scrapy_xc\anjuke_new-data_合并缺少的.txt_去重.txt[F2,F3,F4].txt"

    def start_requests(self):
        headers = self.get_headers(1)
        url = "https://www.baidu.com"
        yield scrapy.Request(url=url, method="GET",callback=self.seed_requests, headers=headers,dont_filter=True)

    def seed_requests(self, response):
        f = open(self.file_name, "r", encoding="utf-8")
        for i in f:
            name = i.strip().split(",")[0]
            city = i.strip().split(",")[1]
            id_lou = i.strip().split(",")[2]
            headers = self.get_headers(2)
            url = "https://m.anjuke.com/{}/loupan/{}/params/".format(city,id_lou)
            yield scrapy.Request(url=url, method="GET",callback=self.sort_all, headers=headers,meta={"name":name,"city":city,"id_lou":id_lou})

    def sort_all(self,response):
        youxiao = re.search('(lp_name)',response.text)
        name1 = response.meta.get("name")
        city = response.meta.get("city")
        id_lou = response.meta.get("id_lou")
        url = response.request.url
        if youxiao:
            lou_name = response.css(".lp_name").xpath("./text()").get()
            miaoshu_list = response.css(".ptese").xpath("./a/span/text()").getall()
            miaoshu = " ".join(miaoshu_list)
            loucheng = ""
            mianji = ""
            city_info = ""
            match = re.search("cityname : '([^']+)",response.text)
            if match:
                city_info =match.group(1)
            danjia = ""
            huxing = ""
            address = ""
            type_lou = ""
            open_time = ""
            area = ""
            info_list = response.css(".info")
            for i in info_list:
                name = i.xpath("./label/text()").get("")
                value = i.xpath("./span/text()").get("")
                if "楼层状况" in name:
                    loucheng = value
                elif "建筑面积" in name:
                    mianji = value
                elif "参考单价" in name:
                    danjia = value
                elif "在售户型" in name:
                    huxing = value
                elif "售楼地址" in name:
                    address = value
                elif "建筑类型" in name:
                    type_lou = value.strip()
                elif "最新开盘" in name:
                    open_time = value
                elif "楼盘地址" in name:
                    area = value
            item = GmWorkItem()
            item["id_lou"] = id_lou
            item["lou_name"] = lou_name
            item["miaoshu"] = miaoshu
            item["loucheng"] = loucheng
            item["mianji"] = mianji
            item["city_info"] = city_info
            item["danjia"] = danjia
            item["huxing"] = huxing
            item["address"] = address
            item["type_lou"] = type_lou
            item["url"] = url
            item["open_time"] = open_time
            item["area"] = area
            item["name1"] = name1
            yield item
        else:
            try_result = self.try_again(response, name=name1,city=city,id_lou=id_lou)
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
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''Host: m.anjuke.com
Connection: keep-alive
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
pragma: no-cache
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        return headers_todict(headers)
