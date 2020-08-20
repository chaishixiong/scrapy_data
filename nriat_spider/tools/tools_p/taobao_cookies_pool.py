from tools.tools_d.account_pool import AccountPool
import requests
import time
from tools.tools_r.taobao.taobao_sign_h5 import get_taobaosign
from tools.tools_r.header_tool import reqhead_split
from tools.tools_r.header_tool import headers_todict

class TaobaoCookies(AccountPool):

    def __init__(self,key):
        super().__init__(key=key,password="nriat.123456")

    #将cookies加入到pool中
    def add_cookies(self):
        cookies = self.cookies_generate()
        if cookies:
            data = self.dumps(cookies)
            self.push_l(self.key,data)

    def get_cookies(self):
        data = self.get_l(self.key)
        if data:
            cookies = self.loads(data)
            return cookies,data

    #淘宝cookies生成方式
    def cookies_generate(self):
        headers = self.get_taobao_headers(1)
        url = "https://h5api.m.taobao.com/h5/mtop.taobao.hacker.finger.create/1.0/?jsv=2.4.11&appKey={}&t={}&sign={}&api=mtop.taobao.hacker.finger.create&v=1.0&type=jsonp&dataType=jsonp&timeout=5000&callback=mtopjsonp1&data=%7B%7D"
        time_now = str(int(time.time() * 1000))
        appkey = "12574478"
        data = '{}'
        sign = get_taobaosign(time=time_now, appKey=appkey, data=data)
        url = url.format(appkey, time_now, sign)
        try:
            req = requests.get(url=url, headers=headers)
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

    def taobao_test(self,goods_id):
        headers = self.get_taobao_headers(2)
        cookies = self.cookies_generate()#这里获取cookies
        print(cookies)

        headers["cookie"] = "t={}; _m_h5_tk={}; _m_h5_tk_enc={}".format(cookies.get("t"),cookies.get("_m_h5_tk"),cookies.get("_m_h5_tk_enc"))
        time_now = str(int(time.time() * 1000))
        appkey = "12574478"
        data = '{{"itemNumId":"{}"}}'.format(goods_id)
        sign_token = cookies.get("_m_h5_tk").split("_")[0]
        sign = get_taobaosign(time=time_now, appKey=appkey, data=data, token=sign_token)
        url = "https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?jsv=2.4.8&appKey={}&t={}&sign={}&api=mtop.taobao.detail.getdetail&v=6.0&dataType=jsonp&ttid=2017%40taobao_h5_6.6.0&AntiCreep=true&type=jsonp&callback=mtopjsonp2&data=%7B%22itemNumId%22%3A%22{}%22%7D"

        for i in [571593162298,533586591285,603317363880,571173957477,579082299554,575655313402,600723610325,582374782414,575099916775,600943798844,556875305433]:
            headers["referer"] = "https://detail.m.tmall.com/item.htm?id={}".format(i)
            url_q = url.format(appkey, time_now, sign, i)
            req = requests.get(url=url_q,headers=headers)
            if "调用成功" in req.text:
                print("请求成功")

    def get_taobao_headers(self,type=1):
        if type==1:
            headers = headers_todict('''accept: */*
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    referer: https://h5.m.taobao.com/applink/smb-fid-sender.html
    sec-fetch-mode: no-cors
    sec-fetch-site: same-site
    user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1''')
        else:
            headers = headers_todict('''accept: */*
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    sec-fetch-mode: no-cors
    sec-fetch-site: cross-site
    user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1''')
        return headers

if __name__=="__main__":
    a = TaobaoCookies("taobao_cookies")
    a.add_cookies()
    cookies,data = a.get_cookies()
    a.rem_l(a.key,data)
    print(cookies)
    print(data)
    print(len(a))