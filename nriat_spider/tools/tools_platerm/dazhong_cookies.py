import random
import time
def random_fun():
    return random.random().hex().replace("x1.","").replace("p-1","")

def Xi():
    t = int(time.time()*1000)
    n = 0
    while int(time.time()*1000) == t and n < 200:
        n += 1
    return hex(t).replace("0x","")+hex(n).replace("0x","")

def screen(height,width):
    return hex(height*width).replace("0x","")

def fun1(t, n):
    r = 0
    for i in range(len(n)):
        r |= n[i] << 8 * i
    return t ^ r
def fun2(ua):
    list_unicode = []
    r = 0
    for i in ua:
        list_unicode.insert(0,255&ord(i))
        if 4 <= len(list_unicode):
            r = fun1(r, list_unicode)
            list_unicode = []
    else:
        if len(list_unicode) > 0:
            r =fun1(r, list_unicode)
        return hex(r).replace("0x","")

def get_prame_dazhong(ua,height=812,width=375):
    return "{}-{}-{}-{}-{}".format(Xi(),random_fun(),fun2(ua),screen(height,width),Xi())

if __name__=="__main__":
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    print(get_prame_dazhong(ua))