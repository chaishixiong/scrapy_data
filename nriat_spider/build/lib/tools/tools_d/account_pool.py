import redis
import sys
import pickle

class AccountPool():
    def __init__(self,key="",host="127.0.0.1",port="6379",password=None):
        self.server = redis.Redis(host=host,port=port,password=password)
        self.key = key

    def __len__(self):
        return self.server.llen(self.key)

    def file_create(self,file_name,key,type="set"):
        self.server.delete(key)#清空redis的队列，将文件的数据加入到队列中
        try:
            with open(file_name,"r",encoding="utf-8") as f:
                for i in f:
                    data = i.strip()
                    if type=="set":
                        self.server.sadd(key,data)
                    elif type=="list":
                        self.server.lpush(key,data)
        except Exception as e:
            print(e)


    def cookies_generate(self):#用来生成cookies的生成方法
        raise Exception("{} no cover".format(sys._getframe().f_code.co_name))

    def general_gennerate(self,*args):
        raise Exception("{} no cover".format(sys._getframe().f_code.co_name))

    def pop_priority(self,key):#有优先级的pool数据获取方式
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(key, 0, 0).zremrangebyrank(key, 0, 0)
        results, count = pipe.execute()
        if results:
            return results[0]

    def get_priority(self,key):
        pass

    def push_priority(self,key, data, score):
        self.server.zadd(key, {data:score})

    def get_hash(self,key):#有映射关系的pool数据获取方式，入对应ip和cookies
        pass

    def pop(self,key):#set
        data = self.server.spop(key)
        return data

    def push(self,key,data):
        self.server.sadd( key, data)

    def push_l(self,key,data):
        self.server.lpush(key,data)

    def get_l(self,key):
        pipe = self.server.pipeline()
        pipe.multi()
        data = self.server.rpop(key)
        if data:
            self.push_l(key,data)
            pipe.execute()
            return data
        else:
            pipe.execute()

    def rem_l(self,key,value):
        self.server.lrem(key,1,value)

    def key_safe_cache(self,key,key_cache):#从主键拿出来，放入缓存
        pipe = self.server.pipeline()
        pipe.multi()
        data = self.pop(key)
        if data:
            self.push(key_cache,data)
            pipe.execute()
            return data
        else:
            pipe.execute()

    def clear_cache(self,key_cache,key):
        check_cache_queue = self.server.scard(key_cache)
        if check_cache_queue > 0:
            using_data = self.server.smembers(key_cache)
            print('-----清理缓存队列-----')
            for i in using_data:
                self.server.sadd(key, i)
                self.server.srem(key_cache, i)

    def loads(self,s):
        return pickle.loads(s)

    def dumps(self,obj):
        return pickle.dumps(obj, protocol=-1)