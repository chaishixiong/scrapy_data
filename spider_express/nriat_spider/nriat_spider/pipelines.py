# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import re
import socket
from pymongo.errors import PyMongoError
import pymongo
import logging
import time
from tools.tools_data.format import format_string
from tools.tools_redis.lock import distributed_lock

logger = logging.getLogger(__name__)


class NriatSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline(object):
    def __init__(self,settings):
        self.settings = settings
        self.limit_num = settings.get("LIMIT_NUM_DATA")
        self.machine = self.get_ip()
        self.time_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = settings.get("SAVE_PATH")


    def get_ip(self):
        addrs = socket.getaddrinfo(socket.gethostname(), "")
        match = re.search("'192.168.\d+.(\d+)'", str(addrs))
        ip_num = "000"
        if match:
            ip_num = match.group(1)
        return ip_num
    def open_spider(self, spider):

        self.name = spider.name
        self.files = dict()
        self.nums = defaultdict(int)
        self.path_spider = Path(self.path)/(spider.name+"-data")
        if not os.path.exists(self.path_spider):
            os.mkdir(self.path_spider)

    def close_spider(self, spider):
        for i in self.files:
            file_name = self.files[i].name
            finish_name = file_name.replace(".txt", "_ok.txt")
            self.files[i].close()
            os.rename(file_name, finish_name)

    def process_item(self, item, spider):
        if "source_code" not in item and "error_id" not in item:
            pipeline_level = item.get("pipeline_level","")
            if self.files.get(pipeline_level):
                file_data = self.files.get(pipeline_level)
            else:
                filedata_name = self.path_spider/(self.time_str + self.name + pipeline_level + self.machine)
                os.mkdir(filedata_name)
                file_data = open(filedata_name / '1-{}.txt'.format(self.limit_num), 'a+', encoding="utf-8")
                self.files[pipeline_level] = file_data

            self.nums[pipeline_level] += 1
            num = self.nums[pipeline_level]
            if num % self.limit_num == 1 and num != 1:
                file_name = file_data.name
                finish_name = file_name.replace(".txt","_ok.txt")
                new_filename = Path(file_data.name)
                file_data.close()
                os.rename(file_name, finish_name)
                file_data = open(new_filename.parent / '{}-{}.txt'.format(num,num+self.limit_num-1), 'a+', encoding="utf-8")
                self.files[pipeline_level] = file_data
            data_list = []
            if "pipeline_level" in item:
                item.pop("pipeline_level")
            for key in item:
                data = item.get(key)
                if data:
                    data = str(data).replace(",","，")
                    data = data.replace("\n", "")
                    data = data.replace("\r", "")
                else:
                    data = ""
                data_list.append(data)
            if data_list:
                data_str = ",".join(data_list)+"\n"
                file_data.write(data_str)
                file_data.flush()
        return item
    @classmethod
    def from_crawler(cls,crawler):
        settings = crawler.settings
        return cls(settings)

class CodeWriterPipeline(object):

    def __init__(self,settings):
        self.settings = settings
        self.limit_num = settings.get("LIMIT_NUM_CODE")
        self.machine = self.get_ip()
        self.time_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = settings.get("SAVE_PATH")

    def get_ip(self):
        addrs = socket.getaddrinfo(socket.gethostname(), "")
        match = re.search("'192.168.\d+.(\d+)'", str(addrs))
        ip_num = "000"
        if match:
            ip_num = match.group(1)
        return ip_num

    def open_spider(self, spider):
        self.name = spider.name
        self.files = dict()
        self.nums = defaultdict(int)
        self.path_spider = Path(self.path)/(spider.name+"-code")
        if not os.path.exists(self.path_spider):
            os.mkdir(self.path_spider)

    def close_spider(self, spider):
        for i in self.files:
            file_name = self.files[i].name
            finish_name = file_name.replace(".txt", "_ok.txt")
            self.files[i].close()
            os.rename(file_name, finish_name)

    def process_item(self, item, spider):
        if "source_code" in item:
            pipeline_level = item.get("pipeline_level","")
            if self.files.get(pipeline_level):
                file_code = self.files.get(pipeline_level)
            else:
                filedata_name = self.path_spider /("code"+ self.time_str + self.name + pipeline_level + self.machine)
                os.mkdir(filedata_name)
                file_code = open(filedata_name / '1-{}.txt'.format(self.limit_num), 'a+', encoding="utf-8")
                self.files[pipeline_level] = file_code
            self.nums[pipeline_level] += 1
            num = self.nums[pipeline_level]

            if num % self.limit_num == 1 and num != 1:
                file_name = file_code.name
                finish_name = file_name.replace(".txt","_ok.txt")
                new_filename = Path(file_code.name)
                file_code.close()
                os.rename(file_name,finish_name)
                file_code = open(new_filename.parent / '{}-{}.txt'.format(num,num+self.limit_num-1), 'a+',encoding="utf-8")
                self.files[pipeline_level] = file_code

            data_list = []
            if "pipeline_level" in item:
                item.pop("pipeline_level")
            for key in item:
                data = item.get(key)
                if data:
                    data = str(data).replace(",","，")
                    data = data.replace("\n", "")
                    data = data.replace("\r", "")
                else:
                    data = ""
                data_list.append(data)
            if data_list:
                data_str = ",".join(data_list)+"\n"
                file_code.write(data_str)
                file_code.flush()
        return item
    @classmethod
    def from_crawler(cls,crawler):
        settings = crawler.settings
        return cls(settings)


class MongoWriterPipeline(object):
    def __init__(self,settings):
        self.settings = settings
        self.mongo_url = settings.get("MONGO_URL")
        self.mongo_db = settings.get("MONGO_PROJECT")
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def open_spider(self, spider):
        self.name = spider.name
        self.mongo_num = None

    def close_spider(self, spider):
        self.client.close()

    def try_connect(self):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        if "pipeline_level" in item:
            pipeline_level = item.pop("pipeline_level")
        else:
            pipeline_level = "general"

        if not self.mongo_num:
            mongo_value = format_string().date_num()
            self.mongo_num = distributed_lock().acquire_lock(lock_name=pipeline_level, lock_prefix="mongo:{}:".format(self.name),identifier=mongo_value,time_out=0,acquire_time=1)
            if not self.mongo_num:
                #保存到磁盘
                self.mongo_num = distributed_lock().get_prame(key=pipeline_level, lock_prefix="mongo:{}:".format(self.name))
        collection = "{}_{}_{}".format(self.name,pipeline_level,self.mongo_num)
        try:
            self.db[collection].insert_one(dict(item))
        except PyMongoError as e:
            logging.info(e)

        return item

    def date_creat(self,last_num=1):
        date_format = time.strftime("%Y%m%d",time.localtime())
        num = str(int(date_format)*10000+last_num)
        return num

    @classmethod
    def from_crawler(cls,crawler):
        settings = crawler.settings
        return cls(settings)


