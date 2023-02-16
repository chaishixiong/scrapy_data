import time
import requests
from tools.tools_request.smt.smt_getsign import get_sign
from tools.tools_request.smt.smt_headers import get_headers
from tools.tools_request.header_tool import get_host,reqhead_split



def get_prame(url):
    headers=get_headers()
    req = requests.get(url=url,headers=headers)
    set_cookie = req.headers.get("set-cookie")
    prame = reqhead_split(set_cookie)
    return prame
def get_etag(url):
    url2 = "https://log.mmstat.com/eg.js"
    headers2 = get_headers(2)
    headers2["Host"] = get_host(url2)
    headers2["Referer"] = url
    req2 = requests.get(url=url2,headers=headers2)
    etag = req2.headers.get("ETag")
    if etag:
        etag = etag.replace('"',"")
    return etag

def get_prame3(seller_id,url,prame,etag):
    time_str = int(time.time()*1000)
    appkey = "24770048"
    data = r'''{{"componentKey":"shopHead","params":"{{\"country\":\"US\",\"site\":\"glo\",\"sellerId\":{},\"backgroundHeight\":\"200\",\"backgroundImage\":\"//ae01.alicdn.com/kf/HTB1WkR_d4TpK1RjSZR0762EwXXaL.png\",\"backgroundWidth\":\"720\",\"language\":\"English\",\"loginUserId\":\"0\",\"locale\":\"en_US\",\"shopSignSelected\":\"logo\"}}"}}'''.format(seller_id)
    sign = get_sign(time_str,appkey,data)
    url3 = "https://acs.aliexpress.com/h5/mtop.alibaba.alisite.ae.server.moduleasyncservice/1.0/?jsv=2.4.2&appKey=24770048&t={}&sign={}&api=mtop.alibaba.alisite.ae.server.ModuleAsyncService&v=1.0&dataType=json&type=originaljson&timeout=3000&AntiCreep=true&data={}".format(time_str,sign,data)
    cookies_s = "ali_apache_id={}; xman_us_f=x_l=1; acs_usuc_t={}; xman_t={}; xman_f={}; cna={}".format(prame.get("ali_apache_id"),prame.get("acs_usuc_t"),prame.get("xman_t"),prame.get("xman_f"),etag)
    headers3 = get_headers(3)
    headers3["Host"] = get_host(url3)
    headers3["Referer"] = url
    headers3["Origin"] = "https://m.aliexpress.com"
    headers3["Cookie"] = cookies_s

    req3 = requests.get(url=url3,headers=headers3)
    set_cookie = req3.headers.get("set-cookie")
    prame3 = reqhead_split(set_cookie)
    return prame3

def get_allprame(shop_id,seller_id,url):
    prame = get_prame(url)
    etag = get_etag(url)
    prame3 = get_prame3(seller_id, url, prame, etag)
    if not prame or not etag or not prame3:
        raise Exception("token参数获取错误")
    return prame,etag,prame3