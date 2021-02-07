import pymongo
from tools.tools_data.thread_pool import ThreaPool


class MongoTransfer1(ThreaPool):
    def __init__(self):
        super().__init__()
        mongo_url = "mongodb://localhost:27017"
        self.mongo_project = "spider_general"
        self.mongo_collection = "amazon_shopinfo_test"
        self.split_limit = 8000
        self.client = pymongo.MongoClient(mongo_url)
        self.db = self.client[self.mongo_project]
        self.collection_num = 1000000

    def data_queue(self):
        for i in range(0,self.collection_num+1,self.split_limit):
            self.work_queue.put((self.mongo_find,(),{"skip":i}))

    def mongo_find(self,thread_id,*args,**kwargs):#数据处理的方法
        #？？获取的分块数据的后续处理
        skip = kwargs.get("skip")
        a = self.db[self.mongo_collection].find().limit(self.split_limit).skip(skip)
        data = [i for i in a]
        print("线程{}获取数据大小：".format(thread_id),len(data))

    def mongo_inser(self,data):#data后列表会加入_id
        #插入mongo的异常统计等处理
        self.db[self.mongo_collection].insert_many(data)

    def collection_write(self):
        for j in range(0,500000,8000):
            datas = []
            for i in range(j,j+8000):
                data = {
                    "shop_url": "{}/-/zh/s/ref=sr_in_-2_p_6_0/139-6349579-4462217?fst=as%3Aoff&rh=n%3A2619525011%2Cp_6%3AA3K7H4HX7ZO6HG&bbn=2619525011&ie=UTF8&qid=1611567093&rnid=2661622011".format(i),
                    "shop_id": "{}A3K7H4HX7ZO6HG".format(i),
                    "shop_name": "{}1Stop Lighting".format(i),
                    "goods_num": "{}887".format(i),
                    "sort": "{}Appliances".format(i)
                }
                datas.append(data)
            self.mongo_inser(datas)


if __name__=="__main__":
    a = MongoTransfer1()
    a.thread_pool(10)