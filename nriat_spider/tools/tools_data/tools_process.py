from nriat_spider.tools.tools_data.tools_base import tools_file_b
from pathlib import Path
import numpy as np
import os
import re

class tools_file():

    def saomiao(self,path):  # 扫描的数据过亿，数据太大内存溢出，分段
        data_tools = tools_file_b()
        suffix = ".txt"
        youxiao = "扫描店铺(\d+)-(\d+)}"

        for file_name,match_str in data_tools.listdir(path,youxiao):
            start = int(match_str[0])
            end = int(match_str[1])
            shop_id = data_tools.get_nparray(file_name)
            print("shop_id生成")
            dif = end-start
            if dif < 50000000:
                print(start, end)
                range_num = np.arange(start, start)
                data_shao = np.setdiff1d(range_num, shop_id)
                print("缺少的data生成")
                file = open(path + "\扫描店铺{}-{}缺少的.txt".format(start, end), "a", encoding="utf-8")
                for j in data_shao:
                    file.write(str(j) + "\n")
                pass
            else:
                for i in range(int(dif/10000000)+1):
                    num1 = start + 10000000 * i
                    num2 = start + 10000000 * (i + 1)
                    if num2 > end:
                        num2 = end
                    if num1==num2:
                        break
                    print(num1, num2)
                    range_num = np.arange(num1, num2)
                    data_shao = np.setdiff1d(range_num, shop_id)
                    print("缺少的data生成")
                    file = open(path + "\扫描店铺{}-{}缺少的.txt".format(num1, num2), "a", encoding="utf-8")
                    for j in data_shao:
                        file.write(str(j) + "\n")

    def two_data_p(self,path, file_name1, file_name2, shuchu_name,num=None,num1=None,dict_name="setdiff1d"):
        path_name = Path(path)

        file_seeds = path_name / file_name1
        file_data = path_name / file_name2
        data_tools = tools_file_b()

        shop_seeds = data_tools.get_nparray(file_seeds,num)
        print("种子生成完毕")

        shop_data = data_tools.get_nparray(file_data,num1)
        print("数据生成完毕")
        dict_def ={
            "setdiff1d":np.setdiff1d,
            "intersect1d": np.intersect1d,
            "union1d": np.union1d,
            "setxor1d": np.setxor1d,
        }

        data_shao = dict_def[dict_name](shop_seeds, shop_data)

        print("差值生成完毕")
        file = open(path_name / shuchu_name, "w", encoding="utf-8")
        for j in data_shao:
            file.write(str(j) + "\n")


    def two_data_s(self,path, file_name1, file_name2, shuchu_name,num=None,num1=None):
        path_name = Path(path)

        file_seeds = path_name / file_name1
        file_data = path_name / file_name2
        data_tools = tools_file_b()

        shop_seeds = data_tools.get_dataset(file_seeds,num)
        print("种子生成完毕")

        shop_data = data_tools.get_dataset(file_data,num1)
        print("数据生成完毕")


        data_shao = shop_seeds-shop_data

        print("差值生成完毕")
        file = open(path_name / shuchu_name, "a", encoding="utf-8")
        for j in data_shao:
            file.write(str(j) + "\n")

    def file_write_inset(self,path,file_name_s,data_input,file_name_w,num_seed=None,num_data=0,inornot=True,w_sql = False):
        path_name = Path(path)
        if not w_sql:
            data_input = path_name/data_input

        file_seeds = path_name / file_name_s
        file_write = path_name / file_name_w
        data_tools = tools_file_b()

        data_set = data_tools.get_dataset(file_seeds,num_seed)
        print("set数据生成")
        write_file = open(file_write, "w", encoding="utf-8")

        for i in data_tools.get_yield(data_input):
            if not w_sql:
                data_list = i.strip().split(",")
                data_str = i
            else:
                data_list = i
                try:
                    data_str = ",".join(i)+"\n"
                except:
                    data_list = [str(j) for j in i]
                    data_str = ",".join(data_list)+"\n"

            shop_id = data_list[num_data]  # 判断位置
            if inornot and shop_id and shop_id in data_set:
                write_file.write(data_str)
            if not inornot and shop_id and shop_id not in data_set:
                write_file.write(data_str)


    def file_write_re(self,path,file_name_d,file_name_w,match,num_data=0):
        path_name = Path(path)
        file_data = path_name / file_name_d
        file_write = path_name / file_name_w
        data_tools = tools_file_b()
        write_file = open(file_write, "w", encoding="utf-8")

        for i in data_tools.get_yield(file_data):
            split_data = i.strip().split(",")
            judge = split_data[num_data]  # 判断位置
            if judge and re.search(match,judge):
                write_file.write(i)

    def select_re(self,path,file_name_d,match,num_data=0,split=","):
        path_name = Path(path)
        file_data = path_name / file_name_d
        data_tools = tools_file_b()
        for i in data_tools.get_yield(file_data):
            if split:
                split_data = i.strip().split(split)
            else:
                split_data = [i.strip()]
            judge = split_data[num_data]  # 判断位置
            m = re.search(match, judge)
            if judge and m:
                yield m.group(1),i
            else:
                print(judge)
                yield None,None

    def select_write_re(self,path,file_name_d,file_name_w,match,num_data=0,split=","):
        path_name = Path(path)
        file_write = path_name / file_name_w
        write_file = open(file_write, "w", encoding="utf-8")

        for i in self.select_re(path, file_name_d, match, num_data, split):
            if i:
                write_file.write(i+"\n")

    def file_zip7(self,path,suffix,youxiao,delete=True):
        os.chdir("C:\\Program Files\\7-Zip")#修改为7-Zip目录
        data_tools = tools_file_b()
        for i,_ in data_tools.listdir(path,youxiao):
            data_tools.zip7(i,suffix,delete)