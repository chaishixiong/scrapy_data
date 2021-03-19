from mitmproxy.http import flow
import json
import jsonpath
file = open("./dianping_data.txt","a",encoding="utf-8")
def request(flow:flow):
    if "isoapi" in flow.request.url:
        json_data = json.loads(flow.request.text)
        listData = jsonpath.jsonpath(json_data, "$..listData")
        if listData:
            list = listData[0].get("list")
            recordCount = listData[0].get("recordCount")
            for i in list:
                shop_id = i.get("shopuuid")
                shop_name = i.get("name")
                branchName = i.get("branchName")
                starScore = i.get("starScore")
                reviewCount = i.get("reviewCount")
                priceText = i.get("priceText")
                regionName = i.get("regionName")
                categoryName = i.get("categoryName")
                dishtags = i.get("dishtags")
                hasTakeaway = i.get("hasTakeaway")
                # item["city_name"] = city_name
                # item["cate_name"] = cate_name
                print(recordCount,shop_id,shop_name,branchName,starScore,reviewCount,priceText,regionName,categoryName,dishtags,hasTakeaway)

def response(flow:flow):
    pass
    #mitmdump -q -s mitmproxy_spider.py -p 8080

