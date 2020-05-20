#速卖通vi页获取的参数，19年12月错误失效
import base64
import re
import os
import random
import time

def get_cid():
    random_list = list(os.urandom(16))
    new_list = []
    for i in random_list:
        new_list.append(chr(i))
    str = "".join(new_list)
    cc = str.encode("latin1")
    c = base64.b64encode(cc).decode("utf-8")
    c = c.replace("+","-")
    c = c.replace("/","_")
    c = c.replace("=",".")
    cid = "amp-"+re.sub("\.+$","",c)
    return cid
def get_prama(cid):
    page_id = random.randint(10, 9999)
    time_stamp = int(round(time.time() * 1000))
    str1 = str(page_id)+str(cid)+str(time_stamp)
    return str1
