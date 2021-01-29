import pymysql

sql = '''select shop_id,company,sales_count,sales_money,shop_name,city,county
from tmall_shopinfo_201912 limit 100'''
sql_prame = {
    "host": "192.168.0.228",
    "db": "e_commerce",
    "user": "dev",
    "password": "Data227or8Dev715#"
}

'''insert into {table_name} (field,) value (value1,value2)'''

pymysql.connect()
#获取sql


class MysqlTransfer1():
    def __init__(self,):
        sql_prame = {"host": "192.168.7.104",
        "db": "test",
        "user": "dev",
        "password": "Data227or8Dev715#"}
        self.connect = pymysql.connect(host=sql_prame.get("host"), port=sql_prame.get("port", 3306), db=sql_prame.get("db"),
                                  user=sql_prame.get("user"), password=sql_prame.get("password"), charset="utf8",
                                  use_unicode=True, cursorclass=pymysql.cursors.Cursor)
        mongo_url = "mongodb://localhost:27017"

        self.mongo_project = "spider_general"
        self.mongo_collection = "amazon_shopinfo_test"
        self.split_limit = 8000
        self.client = pymysql.Connect()
        self.db = self.client[self.mongo_project]
        self.collection_num = 1000000
