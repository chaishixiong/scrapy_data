from scrapy_redis.spiders import RedisSpider
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat

class RedisSpiderTryagain(RedisSpider):
    def __init__(self):
        super().__init__()
        self.error_key

    @property
    def error_key(self):
        print("应发错误")
        raise NotImplementedError
    def try_again(self,rsp):
        max_num = 5
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num < max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request
        else:
            request = rsp.request
            request.meta["try_num"] = 0
            obj = request_to_dict(request, self)
            data = picklecompat.dumps(obj)
            try:
                self.server.lpush(self.error_key, data)
            except Exception as e:
                print(e)
