import pymysql

#获取sql


class MysqlTransfer1():
    def __init__(self,):
        self.db = "test"
        self.mtsql_table = "amazon_shopinfo_test"
        sql_prame = {"host": "192.168.7.104",
        "db": "{}".format(self.db),
        "user": "root",
        "password": "hzAllroot"}
        self.connect = pymysql.connect(host=sql_prame.get("host"), port=sql_prame.get("port", 3306), db=sql_prame.get("db"),
                                  user=sql_prame.get("user"), password=sql_prame.get("password"), charset="utf8",
                                  use_unicode=True, cursorclass=pymysql.cursors.Cursor)
        self.cursor = self.connect.cursor()
        self.split_limit = 8000
        self.insert_sql_field = '''insert into {table_name} ({fields}) value ({values})'''
        self.insert_sql = '''insert into {table_name} value ({values})'''
        self.seed_sql = '''select %s from %s'''



    def mysql_find(self,thread_id,*args,**kwargs):#数据处理的方法

        pass
    def mongo_gettableinfo(self):
        mongoinfo = {"_id":"fgsdf","database":"spider_general","tablename":"amazon_test","fields":
            [{"field_name": "shop_url", "field_structure": "varchar", "length": 255},
             {"field_name": "shop_id", "field_structure": "varchar", "length": 255},
             {"field_name": "shop_name", "field_structure": "varchar", "length": 255},
             {"field_name": "goods_num", "field_structure": "varchar", "length": 255}]}
        database = mongoinfo.get("database")
        tablename = mongoinfo.get("tablename")
        fields_info = mongoinfo.get("fields")
        return database,tablename,fields_info

    def creat_table(self,tablename,fields_info):
        field_list = []
        for field_info in fields_info:
            field_name = field_info.get("field_name")
            field_structure = field_info.get("field_structure","varchar")
            field_length = field_info.get("length")
            if field_name:
                structure = field_structure
                if field_length:
                    structure = "{}({})".format(structure,field_length)
                structure_str = "`{}` {} not null".format(field_name,structure)
                field_list.append(structure_str)
        fiilds_structure = ",".join(field_list)
        creat_str = '''create table if not exists `{}`({})ENGINE=MyISAM DEFAULT CHARSET=utf8;'''.format(tablename,fiilds_structure)
        try:
            self.cursor.execute(creat_str)
        except Exception as e:
            #logging()
            return False

    def run(self):
        database, tablename, fields_info = self.mongo_gettableinfo()
        if database and tablename and fields_info:
            self.creat_table(tablename,fields_info)
        else:
            # logging()
            pass

    def mysql_inser(self,data):#data后列表会加入_id
        #插入mongo的异常统计等处理

        self.cursor.execute()

    # class MongoMysql():
    #     def


if __name__ == "__main__":
    MysqlTransfer1().run()