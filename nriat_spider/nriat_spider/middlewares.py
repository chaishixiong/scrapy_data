# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from tools.tools_r.smt.smt_getsign import get_sign
from tools.tools_r.smt.smt_getparam import get_allprame
from tools.tools_r.smt.smt_headers import get_headers
from tools.tools_r.taobao.taobao_sign_h5 import get_taobaosign
from tools.tools_r.header_tool import get_host,headers_todict,reqhead_split,dict_to_cookiesstr
import requests
from scrapy import signals
import os
import re
import time
import types
from copy import deepcopy
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http.response.html import HtmlResponse
import datetime
import random
from tools.tools_p.taobao_cookies_pool import TaobaoCookies,TaobaoLookCookies
from tools.tools_p.dazhong_cookies import get_prame_dazhong
from fake_useragent import UserAgent

class NriatSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class NriatSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class HostDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        url = request.url
        match = re.search("//(.*?)[/$]",url)
        if match:
            host_new = match.group(1)
            request.headers["Host"] = host_new
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UpdatetimeMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def process_request(self, request, spider):
        today = datetime.date.today().strftime("%Y-%m-%d")
        tomorrow = (datetime.date.today()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        data = request.body.decode()
        data = data.replace("入住时间",today)
        data = data.replace("离店时间",tomorrow)
        request._set_body(data)

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

class UserAgentChangeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        request.headers["User-Agent"] = self.ua.random
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    def process_response(self, request, response, spider):
        # 捕获状态码为40x/50x的response
        # if str(response.status).startswith('4') or str(response.status).startswith('5'):
        #     # 随意封装，直接返回response，spider代码中根据url==''来处理response
        #     response = HtmlResponse(url='')
        #     return response

        # 其他状态码不处理
        return response

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            print('Got exception: %s %s' % (request.url,exception))
            # 随意封装一个response，返回给spider
            response = HtmlResponse(url='exception')
            return response

        # 打印出未捕获到的异常
        print('not contained exception: %s' % exception)

class IpChange(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.prame_state = False
        self.location_test = False

    def connect(self):
        name = "宽带连接"
        username = self.username
        password = self.password
        cmd_str = "rasdial %s %s %s" % (name, username, password)
        res = os.system(cmd_str)
        if res == 0:
            print("连接成功")
            return 1
        else:
            print("连接失败")
            return 0

    def disconnect(self):
        name = "宽带连接"
        cmdstr = "rasdial %s /disconnect" % name
        os.system(cmdstr)
        print('断开成功')

    def huan_ip(self):
        if self.location_test:#本地测试不考虑ip变化
            return 1
        else:
            # 断开网络
            self.disconnect()
            # 开始拨号
            state = self.connect()
            return state

    def change_ipandprame(self):
        print("换ip换参数")
        big_change = 0
        while big_change < 5:
            ip_num = 0
            while ip_num < 5:
                time.sleep(2)
                ip_num += 1
                state = self.huan_ip()
                if state:
                    if self.prame_state:
                        prame_state = self.change_prame()
                        if prame_state:
                            return 1#需要变参数时，参数状态为1
                    else:
                        return 1#只需要变参数
            time.sleep(60)
            big_change += 1

    def change_prame(self):
        raise NotImplementedError

class IpChangeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self,crawler):
        self.crawler = crawler
        settings = crawler.settings
        self.num = 0
        self.change_ip = settings.get("CHANGE_IP_NUM")#ip有关的参数
        username = settings.get("USER_NAME")
        password = settings.get("PASSWORD")
        self.IP = IpChange(username,password)
        location_test = settings.get("LOCATION_TEST")
        self.IP.location_test = location_test

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        change_num = self.change_ip
        self.num += 1
        if self.num % change_num == 1:
            self.crawler.engine.pause()
            state = self.IP.change_ipandprame()
            if state:
                self.crawler.engine.unpause()
            else:
                print("ip切换错误：引擎停止")
                self.crawler.engine.close()
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

class SmtPrameDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self,crawler):
        self.num = 0
        self.crawler = crawler
        settings = crawler.settings
        self.change_ip = settings.get("CHANGE_IP_NUM")
        self.username = settings.get("USER_NAME")
        self.password = settings.get("PASSWORD")

    def change_prame(self):
        seller_id = "201122799"
        shop_id = "110173"
        url = "https://m.aliexpress.com/store/v3/home.html?shopId={}&sellerId={}&pagePath=allProduct.htm".format(
            shop_id, seller_id)
        num = 1
        while num < 5:
            num+=1
            try:
                self.prame, self.etag, self.prame3 = get_allprame(shop_id, seller_id, url)  # 这里生成token参数
                break
            except Exception as e:
                print(e)
        else:
            print("参数获取错误超过五次,engine")
            raise Exception()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if spider.name == "smt_goodsid_order" and not request.url.endswith("baidu.com"):
            meta = request.meta
            shop_id = meta.get("shop_id")
            seller_id = meta.get("seller_id")
            page_num = meta.get("page_num")
            self.num += 1
            if self.num % self.change_ip == 1:
                print("换ip换参数")
                self.crawler.engine.pause()
                ip_num = 0
                while ip_num < 5:
                    time.sleep(1)
                    ip_num += 1
                    state = "失败"
                    try:
                        state = self.huan_ip()
                    except Exception as e:
                        print(e)
                    if state == "成功":
                        self.crawler.engine.unpause()
                        break
                    print("换ip错误")
                else:
                    print("ip切换错误：引擎停止")
                    self.crawler.engine.close()
                try:
                    self.change_prame()
                except Exception as e:
                    print("参数切换错误：引擎停止")
                    self.crawler.engine.close()

            prame = self.prame
            etag = self.etag
            prame3 = self.prame3
            url = "https://m.aliexpress.com/store/v3/home.html?shopId={}&sellerId={}&pagePath=allProduct.htm".format(shop_id, seller_id)

            time_str = int(time.time() * 1000)
            appkey = "24770048"
            data = r'''{{"page":{},"pageSize":20,"locale":"en_US","site":"glo","storeId":"{}","country":"US","currency":"USD","aliMemberId":"{}","sort":"orders_desc"}}'''.format(
                page_num, shop_id, seller_id)
            token = prame3.get("_m_h5_tk").split("_")[0]
            sign = get_sign(time_str, appkey, data, token)
            url4 = "https://acs.aliexpress.com/h5/mtop.aliexpress.store.products.search.all/1.0/?jsv=2.4.2&appKey=24770048&t={}&sign={}&api=mtop.aliexpress.store.products.search.all&v=1.0&dataType=json&AntiCreep=true&type=originaljson&data={}".format(
                time_str, sign, data)
            cookies_s = "ali_apache_id={}; xman_us_f=x_l=1; acs_usuc_t={}; xman_t={}; xman_f={}; cna={};_m_h5_tk={}; _m_h5_tk_enc={}".format(
                prame.get("ali_apache_id"), prame.get("acs_usuc_t"), prame.get("xman_t"),
                prame.get("xman_f"), etag, prame3.get("_m_h5_tk"), prame3.get("_m_h5_tk_enc"))
            headers4 = get_headers(3)
            headers4["Host"] = get_host(url4)
            headers4["Referer"] = url
            headers4["Origin"] = "https://m.aliexpress.com"
            headers4["Cookie"] = cookies_s
            request._set_url(url4)
            for i in headers4:
                request.headers[i] = headers4[i]
                # request.headers.setdefault(i,headers4[i])

        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def connect(self):
        name = "宽带连接"
        username = self.username
        password = self.password
        cmd_str = "rasdial %s %s %s" % (name, username, password)
        res = os.system(cmd_str)
        if res == 0:
            print("连接成功")
            return "成功"
        else:
            print("连接失败")
            return "失败"

    def disconnect(self):
        name = "宽带连接"
        cmdstr = "rasdial %s /disconnect" % name
        os.system(cmdstr)
        print('断开成功')

    def huan_ip(self):
        # 断开网络
        self.disconnect()
        # 开始拨号
        a = self.connect()
        return a

class TaobaoLookDownloaderMiddleware(IpChangeDownloaderMiddleware):
    #添加cookies 换 cookies 删cookies
    def __init__(self,crawler):
        super().__init__(crawler)
        self.key = "taobao_look_cookies"
        self.taobao_cookies_p = TaobaoLookCookies(self.key)
        # self.taobao_cookies_p.add_cookies("560650397720")
        self.error_num = 0
        self.headers = self.taobao_cookies_p.get_taobao_headers(2)
        self.url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/?jsv=2.6.1&appKey={}&t={}&sign={}&api=mtop.relationrecommend.WirelessRecommend.recommend&v=2.0&isSec=0&ecode=0&AntiFlood=true&AntiCreep=true&H5Request=true&type=jsonp&dataType=jsonp&callback=mtopjsonp3&data=%7B%22id%22%3A%22{}%22%2C%22appId%22%3A%22766%22%2C%22params%22%3A%22%7B%5C%22itemid%5C%22%3A%5C%22{}%5C%22%2C%5C%22sellerid%5C%22%3A%5C%22{}%5C%22%7D%22%7D"
        self.appkey = "12574478"
        self.error_limit = 30
        self.taobao_cp_limit = 100
        self.ckeck_limit = 100
        self.old_data = None
        self.data = None
        self.time_now = str(int(time.time() * 1000))

    def process_request(self, request, spider):
        change_num = self.change_ip#这里设1000
        goods_id = request.meta.get("goods_id")
        seller_id = request.meta.get("seller_id")
        self.num += 1
        if self.num % change_num == 1 or self.error_num > self.error_limit:#这里的100
            self.crawler.engine.pause()
            self.change_parame()
            if self.error_num <= self.error_limit:
                self.error_num = 0
            state = self.IP.change_ipandprame()
            if state:
                self.crawler.engine.unpause()
            else:
                print("ip切换错误：引擎停止")
                self.crawler.engine.close()

        if self.num % self.ckeck_limit == 0 and len(self.taobao_cookies_p) < self.taobao_cp_limit:
            self.taobao_cookies_p.add_cookies(goods_id)

        if self.error_num > self.error_limit:
            self.taobao_cookies_p.rem_l(self.key,self.old_data)
            self.error_num = 0
            # self.change_parame(goods_id)

        headers = deepcopy(self.headers)
        headers["cookie"] = "_m_h5_tk={}; _m_h5_tk_enc={}".format(self.cookies.get("_m_h5_tk"),self.cookies.get("_m_h5_tk_enc"))
        time_now = str(int(time.time() * 1000))
        data1 = '{{"id":"{}","appId":"766","params":"{{\\"itemid\\":\\"{}\\",\\"sellerid\\":\\"{}\\"}}"}}'.format(goods_id,goods_id,seller_id)
        sign_token = self.cookies.get("_m_h5_tk").split("_")[0]
        sign = get_taobaosign(time=time_now, appKey=self.appkey, data=data1, token=sign_token)

        #請求部分
        headers["referer"] = "https://h5.m.taobao.com/awp/core/detail.htm?id={}".format(goods_id)
        url_q = self.url.format(self.appkey, time_now, sign, goods_id,goods_id,seller_id)
        request._set_url(url_q)
        for i in headers:
            request.headers[i] = headers[i]
        return None

    def change_parame(self):#无需网络
        self.old_data = self.data
        self.cookies, self.data = self.taobao_cookies_p.get_cookies()


    def process_response(self, request, response, spider):
        if "调用成功" not in response.text:
            self.error_num += 1
        return response

class DaZhongDianPingDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    '''
    在换ip之后request换参数
    '''
    def __init__(self,crawler):
        self.num = 0#请求的数量
        self.crawler = crawler
        settings = crawler.settings
        self.prame = None#请求中需要实时带的参数
        self.change_ip = settings.get("CHANGE_IP_NUM")#ip有关的参数
        username = settings.get("USER_NAME")
        password = settings.get("PASSWORD")
        location_test = settings.get("LOCATION_TEST")
        self.IP = IpChange(username,password)
        self.IP.change_prame = types.MethodType(self.change_prame, self.IP)# 将函数run,添加到p1的对象里面。对象里添加函数的方法。
        self.IP.prame_state = True
        self.IP.location_test = location_test

    def change_prame(self,self1):
        self.prame = self.get_sign1()
        if self.prame:
            return 1

    def get_sign1(self):#参数的具体获得
        url = "https://m.dianping.com/quzhou/ch10"
        headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
        Accept-Encoding: gzip, deflate, br
        Accept-Language: zh-CN,zh;q=0.9
        Cache-Control: no-cache
        Connection: keep-alive
        Host: m.dianping.com
        Pragma: no-cache
        Sec-Fetch-Mode: navigate
        Sec-Fetch-Site: none
        Upgrade-Insecure-Requests: 1
        User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        try:
            req = requests.get(url=url, headers=headers_todict(headers))
            headers_rep = req.headers
            set_cookiesstr = headers_rep.get("set-cookie","")
            set_cookies = reqhead_split(set_cookiesstr)
            if set_cookies:
                return set_cookies
        except Exception as e:
            pass

    def request_change(self,request):
        if "isoapi" in request.url:
            city_id = request.meta.get("city_id")
            randomstr = ""
            for i in range(20):
                randomstr += random.choice("0123456789qazwsxedcrfvtgbyhnujmikolp")
            # cookies_dict = {"_hc.v":self.prame.get("_hc.v")}
            cookies_dict = self.prame.copy()
            ua = request.headers.get("User-Agent").decode()
            _lxsdk_cuid = get_prame_dazhong(ua)
            time_Hm = int(time.time()*1000)
            # cookies_dict["_lxsdk_s"]="172554ab5d4-cc7-89c-1f7%7C%7C1"
            cookies_dict["logan_session_token"] = randomstr
            cookies_dict["logan_custom_report"] = ""
            cookies_dict["_lxsdk_cuid"] = _lxsdk_cuid
            cookies_dict["_lxsdk"] = _lxsdk_cuid
            cookies_dict["Hm_lvt_233c7ef5b9b2d3d59090b5fc510a19ce"] = time_Hm
            cookies_dict["Hm_lpvt_233c7ef5b9b2d3d59090b5fc510a19ce"] = time_Hm
            cookies_dict["cityid"] = city_id

            cookeis = dict_to_cookiesstr(cookies_dict)
            request.headers["Cookie"] = cookeis

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if spider.name == "dianping":
            self.num += 1
            if self.num % self.change_ip == 1:#换ip，换参数
                self.crawler.engine.pause()
                ##换ip
                state = self.IP.change_ipandprame()
                if state:
                    self.crawler.engine.unpause()
                else:
                    print("ip，参数切换错误：引擎停止")
                    self.crawler.engine.close()
            self.request_change(request)
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

class TaobaoZhiboDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self,crawler):
        self.num = 0
        self.crawler = crawler
        settings = crawler.settings
        self.cookies_dict = None
        self.change_ip = settings.get("CHANGE_IP_NUM")#ip有关的参数
        username = settings.get("USER_NAME")
        password = settings.get("PASSWORD")
        location_test = settings.get("LOCATION_TEST")
        self.IP = IpChange(username,password)
        self.IP.change_prame = types.MethodType(self.change_prame, self.IP)  # 将函数run,添加到p1的对象里面。对象里添加函数的方法。
        self.IP.prame_state = True
        self.IP.location_test = location_test


    def change_prame(self, self1):
        test_id = "1714128138"
        self.cookies_dict = self.get_sign1(test_id)
        if self.cookies_dict:
            return 1


    def get_sign1(self,sellerid):
        headers1 = self.get_taobao_headers()
        headers1["referer"] = "https://h5.m.taobao.com/taolive/video.html?id={}".format(sellerid)
        url = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.live.videolist/2.0/?jsv=2.4.0&appKey={}&t={}&sign={}&AntiCreep=true&api=mtop.mediaplatform.live.videolist&v=2.0&type=jsonp&dataType=jsonp&timeout=20000&callback=mtopjsonp1&data=%7B%7D"
        time_now = str(int(time.time() * 1000))
        appkey = "12574478"
        data = '{}'
        sign = get_taobaosign(time=time_now, appKey=appkey, data=data)
        url = url.format(appkey, time_now, sign)
        try:
            req = requests.get(url=url, headers=headers1)
            headers_rep = req.headers
            set_cookiesstr = headers_rep.get("set-cookie")
            set_cookies = reqhead_split(set_cookiesstr)
            cookies_dict = dict()
            cookies_dict["t"] = set_cookies.get("t", "")
            cookies_dict["_m_h5_tk"] = set_cookies.get("_m_h5_tk", "")
            cookies_dict["_m_h5_tk_enc"] = set_cookies.get("_m_h5_tk_enc", "")
            if cookies_dict.get("_m_h5_tk") and cookies_dict.get("_m_h5_tk_enc"):
                return cookies_dict
        except Exception as e:
            pass

    def get_taobao_headers(self):
        headers = '''accept: */*
        accept-encoding: gzip, deflate, br
        accept-language: zh-CN,zh;q=0.9
        cache-control: no-cache
        pragma: no-cache
        sec-fetch-mode: no-cors
        sec-fetch-site: same-site
        user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
        return headers_todict(headers)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if (spider.name == "taobao_zhiboinfo" or spider.name == "taobao_goodsid") and not request.url.endswith("baidu.com"):
            meta = request.meta
            self.num += 1
            if self.num % self.change_ip == 1:
                self.crawler.engine.pause()
                state = self.IP.change_ipandprame()
                if state:
                    self.crawler.engine.unpause()
                else:
                    print("参数切换错误：引擎停止")
                    self.crawler.engine.close()
            if spider.name == "taobao_zhiboinfo":
                sellerid = meta.get("seller_id")
                headers2 = self.get_taobao_headers()
                headers2["referer"] = "https://tblive.m.taobao.com/wow/tblive/act/host-detail?wh_weex=true&broadcasterId={}".format(sellerid)  # broadcasterId
                cookeis = dict_to_cookiesstr(self.cookies_dict)
                headers2["Cookie"] = cookeis
                time_now = str(int(time.time() * 1000))
                appkey = "12574478"
                data = '{{"broadcasterId":"{}","start":0,"limit":10}}'.format(sellerid)  #broadcasterId
                sign_token = self.cookies_dict.get("_m_h5_tk").split("_")[0]
                sign = get_taobaosign(time=time_now, appKey=appkey, data=data, token=sign_token)
                url2 = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.anchor.info/1.0/?jsv=2.4.8&appKey={}&t={}&sign={}&api=mtop.mediaplatform.anchor.info&v=1.0&AntiCreep=true&AntiFlood=true&type=jsonp&dataType=jsonp&callback=mtopjsonp3&data=%7B%22broadcasterId%22%3A%22{}%22%2C%22start%22%3A0%2C%22limit%22%3A10%7D"
                url2 = url2.format(appkey, time_now, sign, sellerid)
                request._set_url(url2)
                for i in headers2:
                    request.headers[i] = headers2[i]
            elif spider.name=="taobao_goodsid":
                live_id = meta.get("live_id")
                seller_id = meta.get("seller_id")
                headers2 = self.get_taobao_headers()
                headers2["referer"] = "https://h5.m.taobao.com/taolive/video.html?id={}".format(live_id)  # broadcasterId
                cookeis = dict_to_cookiesstr(self.cookies_dict)
                headers2["Cookie"] = cookeis
                time_now = str(int(time.time() * 1000))
                appkey = "12574478"
                data = '{{"type":"0","liveId":"{}","creatorId":"{}"}}'.format(live_id,seller_id)  #broadcasterId
                sign_token = self.cookies_dict.get("_m_h5_tk").split("_")[0]
                sign = get_taobaosign(time=time_now, appKey=appkey, data=data, token=sign_token)
                url2 = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.video.livedetail.itemlist/1.0/?jsv=2.4.0&appKey={}&t={}&sign={}&AntiCreep=true&api=mtop.mediaplatform.video.livedetail.itemlist&v=1.0&type=jsonp&dataType=jsonp&callback=mtopjsonp4&data=%7B%22type%22%3A%220%22%2C%22liveId%22%3A%22{}%22%2C%22creatorId%22%3A%22{}%22%7D"
                url2 = url2.format(appkey, time_now, sign, live_id,seller_id)
                request._set_url(url2)
                for i in headers2:
                    request.headers[i] = headers2[i]
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class TaobaoGoodsDownloaderMiddleware(IpChangeDownloaderMiddleware):
    #添加cookies 换 cookies 删cookies
    def __init__(self,crawler):
        super().__init__(crawler)
        self.key = "taobao_cookies"
        self.taobao_cookies_p = TaobaoCookies(self.key)
        self.taobao_cookies_p.add_cookies()
        self.error_num = 0
        self.headers = self.taobao_cookies_p.get_taobao_headers(2)
        self.url = "https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?jsv=2.4.8&appKey={}&t={}&sign={}&api=mtop.taobao.detail.getdetail&v=6.0&dataType=jsonp&ttid=2017%40taobao_h5_6.6.0&AntiCreep=true&type=jsonp&callback=mtopjsonp2&data=%7B%22itemNumId%22%3A%22{}%22%7D"
        self.appkey = "12574478"
        self.error_limit = 30
        self.taobao_cp_limit = 100
        self.ckeck_limit = 100
        self.old_data = None
        self.data = None
        self.time_now = str(int(time.time() * 1000))

    def process_request(self, request, spider):
        change_num = self.change_ip#这里设1000
        goods_id = request.meta.get("goods_id")
        self.num += 1
        # if self.num == 1:
        #     self.change_parame(goods_id)
        if self.num % change_num == 1 or self.error_num > self.error_limit:#这里的100
            self.crawler.engine.pause()
            self.change_parame(goods_id)
            if self.error_num <= self.error_limit:
                self.error_num = 0
            state = self.IP.change_ipandprame()
            if state:
                self.crawler.engine.unpause()
            else:
                print("ip切换错误：引擎停止")
                self.crawler.engine.close()

        if self.num % self.ckeck_limit == 0 and len(self.taobao_cookies_p) < self.taobao_cp_limit:
            self.taobao_cookies_p.add_cookies()
            # p = Process(target=self.taobao_add, args=(self.key,))
            # p.start()

        if self.error_num > self.error_limit:
            self.taobao_cookies_p.rem_l(self.key,self.old_data)
            self.error_num = 0
            # self.change_parame(goods_id)

        #請求部分
        self.headers["referer"] = "https://detail.m.tmall.com/item.htm?id={}".format(goods_id)
        url_q = self.url.format(self.appkey, self.time_now, self.sign, goods_id)
        request._set_url(url_q)
        for i in self.headers:
            request.headers[i] = self.headers[i]

        return None

    def change_parame(self,goods_id):#无需网络
        self.old_data = self.data
        self.cookies, self.data = self.taobao_cookies_p.get_cookies()
        self.headers["cookie"] = "t={}; _m_h5_tk={}; _m_h5_tk_enc={}".format(self.cookies.get("t"),
                                                                             self.cookies.get("_m_h5_tk"),
                                                                             self.cookies.get("_m_h5_tk_enc"))
        self.time_now = str(int(time.time() * 1000))
        self.data1 = '{{"itemNumId":"{}"}}'.format(goods_id)
        self.sign_token = self.cookies.get("_m_h5_tk").split("_")[0]
        self.sign = get_taobaosign(time=self.time_now, appKey=self.appkey, data=self.data1, token=self.sign_token)

    def process_response(self, request, response, spider):
        if "调用成功" not in response.text:
            self.error_num += 1
        return response


    # @staticmethod
    # def taobao_add(taobao_cookies):
    #     taobao_cookies_p = TaobaoCookies(taobao_cookies)
    #     taobao_cookies_p.add_cookies()
