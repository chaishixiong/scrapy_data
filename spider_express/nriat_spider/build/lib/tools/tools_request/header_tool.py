import re

def headers_todict(header_str):
    header = header_str.split("\n")
    headers = {}
    for cookie in header:
        if ":" in cookie:
            cookie_split = cookie.split(":",1)
            name = cookie_split[0].strip()
            values = cookie_split[1].strip()
            headers[name] = values
        else:
            headers[cookie] = ""
    return headers

def cookies_split(cookie_str):
    cookies = cookie_str.split(";")
    for cookie in cookies:
        if "=" in cookie:
            cookie_split = cookie.split("=", 1)
            name = cookie_split[0].strip()
            values = cookie_split[1].strip()
            yield name + "=" + values
        else:
            yield cookie.strip()

def dict_to_cookiesstr(cookies_dict):
    cookies_str = "; ".join("{}={}".format(i,y) for i,y in cookies_dict.items())
    return cookies_str

def reqhead_split(headers_str):
    b = re.sub("(expires=[^,]*),", "\\1，", headers_str, flags=re.I)
    h_list = b.split(",")
    dict_p ={}
    for str_p in h_list:
        parameter = str_p.split(";")[0]
        parameter_l = parameter.split("=",1)
        value_p = ""
        if len(parameter_l) > 1:
            value_p = parameter_l[1].strip()
        name_p = parameter_l[0].strip()
        dict_p[name_p] = value_p
    return dict_p

def get_host(url):
    match = re.search("//(.*?)/|//(.*?)$",url)
    host_new = ""
    if match:
        host_new = match.groups()
    for i in host_new:
        if i:
            return i