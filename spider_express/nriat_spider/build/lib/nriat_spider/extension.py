import logging
import time
from pathlib import Path
from scrapy import signals
from scrapy.exceptions import NotConfigured
from nriat_spider.seed_split import file_split
import os
import re
from scrapy_redis import connection
from scrapy.utils.reqser import request_to_dict
from scrapy_redis import picklecompat
from tools.tools_redis.lock import distributed_lock

logger = logging.getLogger(__name__)

class redisSpiderSmartIdleExensions():
    '''
    种子文件的切分
    文件数据自动更新到队列中
    自动关闭没队列的spider任务
    '''
    def __init__(self,settings,crawler):
        self.crawler = crawler
        self.idle_number = settings.getint('IDLE_NUMBER',120)#IDLE关闭等待的次数 5*120 600
        self.idle_check = settings.getint("IDLE_CHECK",3)#idle检查的次数
        self.idle_list = []
        self.idle_count = 0
        self.file_over = False
        self.path_base = settings.get("SEED_FILE_PATH")#种子所在path
        self.path_split = None#分割的文件所在位置
        self.split_num = settings.get("SPLIT_NUM")
        self.server = connection.from_settings(settings)#这里
        self.lock = distributed_lock(self.server)
        self.lock_acquire = 5
        self.lock_outtime = 120
        self.seed_exists = None
        self.key_request = ""

        # self.request_count = settings.getint('MYEXT_ITEMCOUNT', 1000)
        # self.request_num = 0
        # use_set = settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        # request_set = settings.get("SCHEDULER_QUEUE_CLASS")#request获取方式
        # self.fetch_one = self.server.spop if use_set else self.server.lpop
        # self.add_one = self.server.sadd if use_set else self.server.lpush
        # self.get_num = self.server.llen if "LifoQueue" in request_set or "FifoQueue" in request_set else self.server.zcard
        # self.get_startnum = self.server.scard if use_set else self.server.llen


    @classmethod
    def from_crawler(cls, crawler):
        # 首先检查是否应该启用和提高扩展
        # 否则不配置
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        if not 'redis_key' in crawler.spidercls.__dict__.keys():
            raise NotConfigured('Only supports RedisSpider')

        # 获取配置中的时间片个数，默认为360个，30分钟
        settings = crawler.settings
        # scheduler_cls = load_object(crawler.settings['SCHEDULER'])
        # scheduler = scheduler_cls.from_crawler(crawler)
        # 实例化扩展对象
        ext = cls(settings,crawler)
        # 将扩展对象连接到信号， 将signals.spider_idle 与 spider_idle() 方法关联起来。
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)

        # return the extension object
        return ext

    def spider_opened(self, spider):
        self.key_request = "{}:requests".format(spider.name)
        logger.info("opened spider {} redis spider Idle, Continuous idle limit： {}".format(spider.name, self.idle_number))
        self.seed_exists = os.path.exists(Path(self.path_base)/"{}.txt".format(spider.name))
        if self.seed_exists:
            # self.key_start = "{}:start_url".format(spider.name)
            spider.log("opened spider %s" % spider.name)
            file = spider.name + ".txt"
            self.path_split = Path(self.path_base) / (spider.name + "_split")
            result_lock_open = self.lock.acquire_lock(spider.name+"open",self.lock_acquire,0)#建立scrapy文件切分的分布锁
            if result_lock_open:
                split_t = file_split(file=file, path=self.path_base)
                split_t.change_num(self.split_num)
                result = split_t.split()#切分种子
                if result:
                    spider.log("%s spider split success" % spider.name)
                else:
                    self.lock.release_lock(spider.name+"open",result_lock_open)#这里应该有问题
                    raise Exception("分割文本错误")
            if not spider.server.exists(self.key_request):
                result_lock = self.lock.acquire_lock(spider.name,self.lock_acquire,self.lock_outtime)#加锁
                if result_lock:
                    update_state, file_name = self.check_seed(path=self.path_split)
                    if update_state:
                        self.file_request(key=self.key_request,spider=spider, file_name=file_name)#这里将一个文件内容增加进去
                    else:
                        self.lock.release_lock(spider.name,result_lock)#如果没有文件了，把锁解了
                        self.file_over = True

    def spider_closed(self, spider):
        #关闭之后将pipeline中的文件合并
        logger.info("closed spider %s, idle count %d , Continuous idle count %d",
                    spider.name, self.idle_count, len(self.idle_list))

    def spider_idle(self, spider):#改为判断是否有key
        self.idle_count += 1  # 空闲计数
        self.idle_list.append(time.time())  # 每次触发 spider_idle时，记录下触发时间戳
        # idle_list_len = len(self.idle_list)  # 获取当前已经连续触发的次数
        if self.seed_exists:
            # 判断 redis 中是否存在关键key, 如果key被用完，则key就会不存在
            if len(self.idle_list) >= self.idle_check and not spider.server.exists(self.key_request) and not self.file_over:
                #种子文件检测更新
                update_state, file_name = self.check_seed(path=self.path_split)
                if update_state:
                    result_lock = self.lock.acquire_lock(spider.name, self.lock_acquire, self.lock_outtime)
                    if result_lock:
                        self.file_request(key=self.key_request,spider=spider, file_name=file_name)#这里将一个文件内容增加进去
                        #idle参数初始化
                        self.idle_list = [self.idle_list[-1]]
                else:
                    # if result_lock:
                    #     self.lock.release_lock(spider.name,result_lock)
                    self.file_over = True
        if len(self.idle_list) >= 2 and self.idle_list[-1] - self.idle_list[-2] > 6:#间隔大于6秒，说明有任务在跑，参数初始化
            self.idle_list = [self.idle_list[-1]]
        if len(self.idle_list) > self.idle_number and not spider.server.exists(self.key_request) and self.file_over:
            # 连续触发的次数达到配置次数后关闭爬虫
            logger.info('\n continued idle number exceed {} Times'
                        '\n meet the idle shutdown conditions, will close the reptile operation'
                        '\n idle start time: {},  close spider time: {}'.format(self.idle_number,
                                                                                self.idle_list[0], self.idle_list[0]))
            # 执行关闭爬虫操作
            self.crawler.engine.close_spider(spider, 'closespider_pagecount')

    def check_seed(self,path):#检查文件种子文件
            files = os.listdir(path)
            for i in files:
                if re.search("-\d+\.txt",i):
                    return True,i
            else:
                return False,""

    def file_request(self,key,spider,file_name,):
        do_filename = file_name.replace(".txt","do.txt")
        os.rename(self.path_split/file_name,self.path_split/do_filename)
        # print(time.time())
        with open(self.path_split/do_filename,"r",encoding="utf-8") as f:
            for i in f:
                url = i.strip()
                # self.add_one(key,url)#这里将一个请求加到redis
                request = spider.make_requests_from_url(url)
                self._request_queue(key,spider,request)
            else:
                print("更新一个种子队列到队列中")
        # print(time.time())
        end_filename = file_name.replace(".txt","end.txt")
        os.rename(self.path_split/do_filename,self.path_split/end_filename)

    def _request_queue(self,key,spider,request):#这里还差一个zset的队列方式
        data = self._encode_request(request, spider)
        try:
            self.server.lpush(key, data)
        except Exception as e:
            print(e)

    @staticmethod
    def _encode_request(request,spider):
        """Encode a request object"""
        obj = request_to_dict(request, spider)
        return picklecompat.dumps(obj)