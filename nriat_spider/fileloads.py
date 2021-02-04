from urllib import parse
import os
import requests
from tools.tools_request.header_tool import headers_todict
import re
import time

file_dict1={"url":"&mimeType=application%2Fx-upload-data",
"exe":"&mimeType=application%2Foctet-stream",
"xmind":"&mimeType=application%2Fx-upload-data",
"doc":"&mimeType=application%2Fmsword",
"docx":"&mimeType=application%2Fvnd.openxmlformats-officedocument.wordprocessingml.document",
"pptx":"&mimeType=application%2Fvnd.openxmlformats-officedocument.presentationml.presentation",
"xls":"&mimeType=application%2Fvnd.ms-excel",
"xlsx":"&mimeType=application%2Fvnd.openxmlformats-officedocument.spreadsheetml.sheet",
"jpeg":"&mimeType=image%2Fjpeg",
"jpg":"&mimeType=image%2Fjpeg",
"7z":"&mimeType=application%2Fx-upload-data",
"png":"&mimeType=image%2Fpng",
"rar":"&mimeType=application%2Fx-upload-data",
"zip":"&mimeType=application%2Fzip",
"html":"&mimeType=text%2Fhtml",
"md":"&mimeType=application%2Fx-upload-data",
"sh":"&mimeType=application%2Fx-upload-data",
"sql":"&mimeType=application%2Fx-upload-data",
"txt":"&mimeType=text%2Fplain",
"pdf":"&mimeType=application%2Fpdf"}


a = []
with open(r"F:\pycharmproject\spider_express\nriat_spider\conluence.txt","r",encoding="utf-8") as f1:
    num = 0
    for i in f1:
        data = i.strip().split("||")
        match1 = re.search("preview=%2F(\d+)%2F",data[0])
        match2 = re.search("preview=(.*)",data[0])
        match3 = re.search("preview=%2F\d+%2F\d+%2F(.*)",data[0])
        if match1 and match2 and match3:
            num += 1
            pageId = match1.group(1)
            preview = match2.group(1)
            filename_url = match3.group(1)
            filename = data[1].strip()
            a.append((pageId,preview,filename_url,filename))
    print(num)
files_list = os.listdir(r"C:\Users\Administrator\Desktop\geshi")
dict_f = dict()
for i in files_list:
    houzhui = i.split(".")[-1]
    dict_f[houzhui]=i
for i in a:
    pageId, preview, filename_url, filename = i
    # type_file = "pptx"
    # if filename.endswith(type_file):
    houzhui1=filename.split(".")[-1]
    type1 = file_dict1.get(houzhui1)
    if type1:
        file_name1 = dict_f.get(houzhui1)
        with open(r"C:\Users\Administrator\Desktop\geshi\{}".format(file_name1),"rb") as f:
            data_file = f.read()
            len_data = len(data_file)
            file_name2_url = parse.quote(file_name1)

            headers = headers_todict('''Host: 192.168.0.223:8093
        Connection: keep-alive
        Content-Length: {}
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36
        Content-Type: application/octet-stream
        Accept: */*
        Origin: http://192.168.0.223:8093
        Referer: http://192.168.0.223:8093/pages/viewpage.action?pageId={}&preview={}
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9
        Cookie: mywork.tab.tasks=false; JSESSIONID=54A8B74225E15F4213D3E7F84425AFD2'''.format(len_data,pageId,preview))
            url = "http://192.168.0.223:8093/plugins/drag-and-drop/upload.action?pageId={}&filename={}&size={}{}&atl_token=b56c6ae5bad5e41743aa5e579fcf1de761ba6257&withEditorPlaceholder=false&name={}".format(pageId,filename,len_data,type1,file_name2_url)
            proxies = {
                "http": "http://127.0.0.1:8888",
                "https": "http://127.0.0.1:8888",
            }
            # req1 = requests.post(url1,data='[{"name":"confluence-spaces.previews.upload.click","timeDelta":-1706}]',headers=headers1,proxies=proxies)
            req = requests.post(url,data=data_file,headers=headers,proxies=proxies)
            if "data" in req.text:
                print(filename)
        time.sleep(2)
