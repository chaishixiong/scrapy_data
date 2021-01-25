from tools.tools_request.header_tool import headers_todict

def get_headers(type = 1):
    if type == 1:
        headers1 = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        headers1 = headers_todict(headers1)
        return headers1
    elif type == 2:
        headers2 = '''accept: */*
        accept-encoding: gzip, deflate, br
        accept-language: zh-CN,zh;q=0.9
        upgrade-insecure-requests: 1
        user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        headers2 = headers_todict(headers2)
        return headers2
    elif type == 3:
        headers3 = '''Accept: application/json
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1
Content-type: application/x-www-form-urlencoded
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9'''
        headers3 = headers_todict(headers3)
        return headers3