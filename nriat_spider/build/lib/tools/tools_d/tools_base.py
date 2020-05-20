import numpy as np
import os
import re
import csv
from nriat_spider.tools.tools_s.sql_base import get_data


class tools_file_b():
    def get_nparray(self,filename, num=None):
        if num != None:
            with open(filename, "r", encoding="utf-8") as f:
                data = np.array([i.strip().split(",")[num] for i in f])
        else:
            with open(filename, "r", encoding="utf-8") as f:
                data = np.array([i.strip() for i in f])  # 这里保证id为数字
        return data

    def get_dataset(self,filename, num=None):
        data_set = set()
        if num != None:
            with open(filename, "r", encoding="utf-8") as f:
                for i in f:
                    data = i.strip().split(",")[num]
                    if data:
                        data_set.add(data)
        else:
            with open(filename, "r", encoding="utf-8") as f:
                for i in f:
                    data = i.strip()
                    if data:
                        data_set.add(data)
        return data_set

    def get_yield(self,data_input):
        if isinstance(data_input,tuple):
            for i in get_data(data_input[0],data_input[1]):
                yield i
        else:
            with open(data_input, "r", encoding="utf-8") as f:
                for i in f:
                    yield i


    def listdir(self,path, jiaoyan):
        for file in os.listdir(path):
            file_path = os.path.join(path, file)#文件名称
            match = re.search(jiaoyan, file_path)
            if match :
                yield file_path, match.groups()

    def write_csv(self,filename, header, data):
        with open(filename, "w", newline="", encoding="utf-8") as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow(header)
            for i in data:
                csvWriter.writerow(i)

    def zip7(self,file_name,suffix,delete=True):
        try:
            print("正在压缩", file_name)
            new_ys = file_name.replace(suffix, "压缩.7z")
            cmd = "7z.exe a -tzip {} {}".format(new_ys, file_name)
            a = os.popen(cmd)
            console_str = a.read()
            if "Ok" in console_str:
                print("ok")
                if delete:
                    os.remove(file_name)
        except Exception as e:
            print(file_name, e)