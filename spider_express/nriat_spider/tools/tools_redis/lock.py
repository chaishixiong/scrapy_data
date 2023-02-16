#连接redis
import time
import uuid
import redis
from tools.tools_redis.connect import redis_connect

class distributed_lock(redis_connect):

    #获取一个锁
    # lock_name：锁定名称
    # acquire_time: 客户端等待获取锁的时间
    # time_out: 锁的超时时间
    def get_prame(self,key,lock_prefix="string:lock:"):
        lock = lock_prefix + key
        #获取redis中spider pipeline_level是否有该建
        value = self.redis_client.get(lock)
        if value:
            value = value.decode()
        return value

    def acquire_lock(self,lock_name, acquire_time=5, time_out=100,lock_prefix="string:lock:",identifier=None):
        """获取一个分布式锁"""
        if not identifier:
            identifier = str(uuid.uuid4())
        end = time.time() + acquire_time
        lock = lock_prefix + lock_name
        while time.time() < end:
            if self.redis_client.setnx(lock, identifier):
                # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
                if time_out:
                    self.redis_client.expire(lock, time_out)
                return identifier
            # elif not self.redis_client.ttl(lock):
            #     self.redis_client.expire(lock, time_out)
            time.sleep(0.1)
        return False

    #释放一个锁
    def release_lock(self,lock_name, identifier,lock_prefix="string:lock:"):
        """通用的锁释放函数"""
        lock = lock_prefix + lock_name
        pip = self.redis_client.pipeline(True)
        while True:
            try:
                pip.watch(lock)
                lock_value = self.redis_client.get(lock)
                if not lock_value:
                    return True
                if lock_value.decode() == identifier:
                    pip.multi()
                    pip.delete(lock)
                    pip.execute()
                    return True
                pip.unwatch()
                break
            except redis.exceptions.WatchError:
                pass
        return False


if __name__=="__main__":
    a = distributed_lock()
    # a.redis_client=redis.Redis()
    # result = a.acquire_lock("spider",5,50)
    result = a.get_prame("dfsd","")
    # time.sleep(2)
    # a.release_lock("spider",result)
    print(result)