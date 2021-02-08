from nriat_spider.test_mongo import MongoTransfer1
from nriat_spider.test_mysql import MysqlTransferl
from tools.tools_data.thread_pool import ThreaPool


class DataTransferl(ThreaPool):
    def __init__(self):
        super().__init__()
        self.mongotf = MongoTransfer1()
        self.mysqltf = MysqlTransferl()

    def data_queue(self,args=(),kwargs=None):
        if kwargs is None:
            kwargs = []
        for i in range(0,self.mongotf.collection_num+1,self.mongotf.split_limit):
            #put的
            self.work_queue.put((self.mongotf.mongo_find,args,kwargs))

    def run(self):
        database, tablename, fields_info = self.mongotf.mongo_gettableinfo()
        if database and tablename and fields_info:
            self.mysqltf.creat_table(tablename, fields_info)
        else:
            # logging()
            pass