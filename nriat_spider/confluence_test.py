import requests
from tools.tools_request.header_tool import headers_todict
from scrapy import Selector
import time
headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: max-age=0
Connection: keep-alive
Cookie: mywork.tab.tasks=false; JSESSIONID=BFA399ECFE231E327E59D64F9D833A85
Host: 192.168.0.223:8093
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'''
headers = headers_todict(headers)
write_file = open("./conluence.txt","a+",encoding="utf-8")
for i in range(0,1021,10):
    page_url = "http://192.168.0.223:8093/dosearchsite.action?cql=lastmodified+%3E%3D+%222020-04-15%22+and+lastmodified+%3C%3D+%222020-10-05%22+and+type+%3D+%22attachment%22&startIndex={}".format(i)
    print(page_url)
    req = requests.get(url=page_url,headers=headers)
    req_s = Selector(text=req.text)
    node_s = req_s.css(".search-result-link.visitable")
    for i in node_s:
        href = i.xpath("./@href").get("")
        name = i.xpath("./text()").get("")
        write_file.write("{}||{}\r\n".format(href,name))
        write_file.flush()
    time.sleep(3)



