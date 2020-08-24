import time
import requests

from nriat_spider.tools.tools_r.smt.smt_getsign import get_sign
from nriat_spider.tools.tools_r.smt.smt_getparam import get_prame3, get_prame, get_etag
from nriat_spider.tools.tools_r.header_tool import get_host
from nriat_spider.tools.tools_r.smt.smt_headers import get_headers

base_url = "https://acs.aliexpress.com/h5/mtop.aliexpress.store.products.search.all/1.0/?jsv=2.4.2&appKey=24770048&t={}&sign={}&api=mtop.aliexpress.store.products.search.all&v=1.0&dataType=json&AntiCreep=true&type=originaljson&data={}"

# 获取参数data
def get_data(shop_id, seller_id, num=1):
    data = r'''{{"page":{},"pageSize":20,"locale":"en_US","site":"glo","storeId":"{}","country":"US","currency":"USD","aliMemberId":"{}","sort":"orders_desc"}}'''.format(num,shop_id,seller_id)
    return data

# 获取参数t
def get_t():
    t = int(time.time()*1000)
    return t

# 构造url
def get_url(prame3,num=1):

    appkey = "24770048"
    t = get_t()
    data = get_data(shop_id, seller_id, num)

    token = prame3.get("_m_h5_tk").split("_")[0]
    sign = get_sign(t, appkey, data, token)

    url = base_url.format(t, sign, data)
    return url

# 获取数据
def get_response(shop_id,seller_id,url,num=1):
    appkey = "24770048"

    prame = get_prame(url)
    etag = get_etag(url)
    prame3 = get_prame3(seller_id,url,prame,etag)
    url4 = get_url(prame3,num)

    t = get_t()
    data = get_data(shop_id,seller_id,num)
    token = prame3.get("_m_h5_tk").split("_")[0]
    sign = get_sign(t,appkey,data,token)
    # url4 = "https://acs.aliexpress.com/h5/mtop.aliexpress.store.products.search.all/1.0/?jsv=2.4.2&appKey=24770048&t={}&sign={}&api=mtop.aliexpress.store.products.search.all&v=1.0&dataType=json&AntiCreep=true&type=originaljson&data={}".format(t,sign,data)
    cookies_s = "ali_apache_id={}; xman_us_f=x_l=1; acs_usuc_t={}; xman_t={}; xman_f={}; cna={};_m_h5_tk={}; _m_h5_tk_enc={}".format(prame.get("ali_apache_id"),prame.get("acs_usuc_t"),prame.get("xman_t"),prame.get("xman_f"),etag,prame3.get("_m_h5_tk"),prame3.get("_m_h5_tk_enc"))

    headers4 = get_headers(3)
    headers4["Host"] = get_host(url4)
    headers4["Referer"] = url
    headers4["Origin"] = "https://m.aliexpress.com"
    headers4["Cookie"] = cookies_s
    response = requests.get(url=url4,headers=headers4)


    print('正在爬取：%s' % (shop_id))
    print(response.text)


    return response

def parse_num(shop_id, seller_id,num=1):
    response = get_response(num, shop_id, seller_id)
    print(response.text)





if __name__ == '__main__':
    shop_id = '11111'
    seller_id = '202588862'

    url = "https://m.aliexpress.com/store/v3/home.html?shopId={}&sellerId={}&pagePath=allProduct.htm".format(shop_id,seller_id)
    get_response(shop_id,seller_id,url)
    #
    # with open('smt_shopid.txt', 'r') as f:
    #     id = f.readlines(10000)
    # print(len(id))

    # start = time.time()
    # for i in id:
    #     ids = i.replace('\n', '').split(',')
    #     shop_id = ids[0]
    #     seller_id = ids[1]
    #
    #
    # end = time.time()
    # s = end - start
    # print('总时间：%s' % s)

    # ret = data.get("ret")
    # print(num)
    # for i in ret:
    #     id = i.get("id")
    #     orders = i.get("orders")
    #     print(id, orders)
    # for i in range(2, int(totle / 20)):
    #     req4 = get_response(i)
    #     api_data = json.loads(req4.text)
    #     data = api_data.get("data")
    #     totle = data.get("total")
    #     ret = data.get("ret")
    #     for i in ret:
    #         id = i.get("id")
    #         orders = i.get("orders")
    #         print(id, orders)