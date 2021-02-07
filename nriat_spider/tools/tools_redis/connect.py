import redis
from tools.tools_redis.setting import host,port,password,db
class redis_connect():
    def __init__(self,redisclient=None,host=host,port=port,password=password,db=db):
        if redisclient:
            self.redis_client = redisclient
        else:
            self.redis_client = redis.Redis(host=host, port=port, password=password, db=db, )

if __name__=="__main__":
    a = redis_connect()
    print(a.redis_client.get("string:lock:amazon_sortshopopen"))