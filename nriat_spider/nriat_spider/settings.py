# -*- coding: utf-8 -*-

# Scrapy settings for nriat_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time

BOT_NAME = 'nriat_spider'

SPIDER_MODULES = ['nriat_spider.spiders']
NEWSPIDER_MODULE = 'nriat_spider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'gm_work (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4#并发

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1#下载延迟三秒
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "zh-CN,zh;q=0.9",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
# }

# ----------- selenium参数配置 -------------
SELENIUM_TIMEOUT = 25           # selenium浏览器的超时时间，单位秒
#LOAD_IMAGE = True               # 是否下载图片
WINDOW_HEIGHT = 900             # 浏览器窗口大小
WINDOW_WIDTH = 900

# Enable or disable spider middlewares爬虫中间件
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'gm_work.middlewares.AntAppSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares下载中间件
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
MY_USER_AGENT = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
]
DOWNLOADER_MIDDLEWARES = {
#   'gm_work.middlewares.AntAppDownloaderMiddleware': 543,
#   'gm_work.middlewares.RandomUserAgentMiddleware':543,
#   'gm_work.middlewares.ProxyDownloaderMiddleware': 400,
#   'gm_work.middlewares.SeleniumMiddleware': 10,
#   'gm_work.middlewares.HostDownloaderMiddleware': 30,
#   'nriat_spider.middlewares.SmtPrameDownloaderMiddleware': 20,
    'nriat_spider.middlewares.IpChangeDownloaderMiddleware': 20,
    'nriat_spider.middlewares.ProcessAllExceptionMiddleware': 21,
    # 'nriat_spider.middlewares.DaZhongDianPingDownloaderMiddleware': 23,
    #   'nriat_spider.middlewares.UpdatetimeMiddleware': 23,

}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   # 'scrapy.extensions.telnet.TelnetConsole': None,
    'nriat_spider.extension.redisSpiderSmartIdleExensions': 500,
}
# 'gm_work.middlewares.HostDownloaderMiddleware': 500,

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {#从低到高
    'nriat_spider.pipelines.CodeWriterPipeline': 290,
    'nriat_spider.pipelines.JsonWriterPipeline': 300,
    # 'nriat_spider.pipelines.errorWriterPipeline': 310,
    # 'nriat_spider.pipelines.MongoWriterPipeline': 310,
    # 'gm_work.pipelines.MysqlPipeline': 300,
   # 'scrapy_redis.pipelines.RedisPipeline': 290
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []#这么http状态码不响应
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

RETRY_ENABLED = False#重试
RETRY_TIMES = 3
#RETRY_HTTP_CODES=#遇到什么网络状态码进行重试默认[500, 502, 503, 504, 522, 524, 408]
HTTPERROR_ALLOWED_CODES=[301,302,307,403,404,408,429,500, 502, 503, 504, 522, 524] #允许在此列表中的非200状态代码响应
REDIRECT_ENABLED = False##重定向
REDIRECT_MAX_TIMES = 5




DOWNLOAD_TIMEOUT = 15#超时等待时间
#DOWNLOAD_MAXSIZE下载最大相应大小
#DOWNLOAD_WARNSIZE下载警告大小

#log日志记录
LOG_LEVEL = "INFO"
to_day = time.localtime()
log_file_path = 'log/scrapy_{}_{}_{}.log'.format(to_day.tm_year, to_day.tm_mon, to_day.tm_mday)#在spider添加spidername
#LOG_FILE = log_file_path


# COMMANDS_MODULE = "gm_work.commands"#将自定义命令加入到scrapy中
#SPIDER_LOADER_CLASS = ""#这个？


#reids
#指定使用scrapy-redis的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"#指定使用scrapy-redis的去重
# 指定排序爬取地址时使用的队列，
# 默认的 按优先级排序(Scrapy默认)，由sorted set实现的一种非FIFO、LIFO方式。
# 广度优先:"scrapy_redis.queue.FifoQueue  深度优先:"SpiderPriorityQueue LifoQueue  优先： PriorityQueue
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'
REDIS_START_URLS_AS_SET = True
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PARAMS = {'password': 'nriat.123456',}
SCHEDULER_PERSIST = True# 是否在关闭时候保留原来的调度器和去重记录，True=保留，False=清空

# 密码登陆
# REDIS_URL="redis://[user]:password@localhost:port"

MONGO_URL = "mongodb://localhost:27017"
MONGO_PROJECT = "spider_general"



#连接MYSQL数据库
MYSQL_HOST = '192.168.0.227'
MYSQL_PORT = 3306
MYSQL_DBNAME = 'ec_cross_border'
MYSQL_USER = 'dev'
MYSQL_PASSWD = 'Data227or8Dev715#'

#爬行顺序
# DEPTH_PRIORITY = 1#正数以广度优先，加后面两个设置彻底以广度优先
# SCHEDULER_DISK_QUEUE  =  'scrapy.squeues.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE  =  'scrapy.squeues.FifoMemoryQueue'

#extend相关的东西
MYEXT_ENABLED = True      # 开启redis结束的扩展
IDLE_NUMBER = 36           # 配置空闲持续时间单位为 360个 ，一个时间单位为5s
IDLE_CHECK = 3#3个idle检查一次
SEED_FILE_PATH = "W:\scrapy_seed"
SPLIT_NUM = 50000
GET_LOCK_TIME = 5
LOCK_ADDREQUESTS_OUTTIME = 120
# Redis集群地址
# REDIS_MASTER_NODES = [
#     {"host": "192.168.0.230", "port": "6379"},
#     {"host": "192.168.0.225", "port": "6379"},
#     {"host": "192.168.0.226", "port": "6379"},
# ]
#
# # 使用的哈希函数数，默认为6
# BLOOMFILTER_HASH_NUMBER = 6
#
# # Bloomfilter使用的Redis内存位，30表示2 ^ 30 = 128MB，默认为22 (1MB 可去重130W URL)
# BLOOMFILTER_BIT = 22
#
# # 不清空redis队列
# SCHEDULER_PERSIST = True
# # 调度队列
# SCHEDULER = "scrapy_redis_cluster.scheduler.Scheduler"
# # 去重
# DUPEFILTER_CLASS = "scrapy_redis_cluster.dupefilter.RFPDupeFilter"
# # queue
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis_cluster.queue.LifoQueue'


#pipeline
SAVE_PATH = r"W:\scrapy_xc"
LIMIT_NUM_DATA = 10000
LIMIT_NUM_ERROR = 10000
LIMIT_NUM_CODE = 10000
#ip:
CHANGE_IP_NUM = 200

import socket,re
def get_ip():
    addrs = socket.getaddrinfo(socket.gethostname(), "")
    match = re.search("'192.168.(\d+.\d+)'", str(addrs))
    ip_num = "0.000"
    if match:
        ip_num = match.group(1)
    return ip_num
if get_ip() in ["9.10","9.11","9.42","9.127","9.128","10.101","10.102","10.103","10.104","10.105","10.106","10.100","9.97","9.95","9.122","9.68"]:
    USER_NAME = "057762355592"
    PASSWORD = "928858"
elif get_ip() == "9.123":
    USER_NAME = "wzlcb57746616"
    PASSWORD = "123456"
elif get_ip() == "9.124":
    USER_NAME = "wzlcf57746616"
    PASSWORD = "123456"
elif get_ip() == "9.125":
    USER_NAME = "wzlcg57746616"
    PASSWORD = "123456"
elif get_ip() == "9.126":
    USER_NAME = "wzlcc57746616"
    PASSWORD = "123456"
elif get_ip() in ["9.148","9.149","9.170","9.171","9.172","9.173"]:
    USER_NAME = "057764473605"
    PASSWORD = "744523"
else:
    USER_NAME = "057762355594"#9.100 9.99 9.98 0.56 0.59 9.129
    PASSWORD = "045805"
if get_ip() =="0.226" or get_ip() =="7.144":
    LOCATION_TEST = True

#rasdial 宽带连接 wzlcg57746616 123456
#rasdial ADSL 057764473605 744523