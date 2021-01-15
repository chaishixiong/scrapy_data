from pathlib import Path
import os
import re
from collections import defaultdict
import time


class SpiderFileMerge(object):
    def __init__(self, save_path):
        self.save_path = Path(save_path)
        self.finish_list = []

    def finish(self,finish_list):
        self._change_finish(finish_list)
        self.compression()
        for i in finish_list:
            self.merge_file(i)


    def merge_file(self, spider_name):
        path_spider = self.save_path / (spider_name + "-data")
        sortfile_dict = self._get_folder(path_spider)#合并
        for i in sortfile_dict:
            file_list = self._folder_tofile(sortfile_dict.get(i),".txt")
            self._merge_file(self.save_path / (i + ".txt"), file_list)#合并

    def compression(self,compression_str="_ok.txt"):
        folders = os.listdir(self.save_path)
        compression_file = None
        for folder in folders:
            result = self.compression_file(folder,compression_str)
            if result:
                compression_file = True
        if compression_file:
            return True
        else:
            return False

    def compression_file(self,path_name,compression_str):
        file_lists = []
        match = re.search("(.*?-code)$", path_name)
        if match:
            spider_name = match.group(1)
            path_spider = self.save_path / spider_name
            sortfile_dict = self._get_folder(path_spider)  # 合并
            for i in sortfile_dict:
                finish = None
                for j in self.finish_list:
                    if i.startswith(j):
                        finish = True
                        break
                if finish:
                    file_list = self._folder_tofile(sortfile_dict.get(i), ".txt")
                else:
                    file_list = self._folder_tofile(sortfile_dict.get(i), compression_str)
                file_lists.extend(file_list)
        if file_lists:
            self._zip7(file_lists)#压缩
            return True
        else:
            return False

    def _change_finish(self,finish_list):
        self.finish_list = finish_list

    @staticmethod
    def _merge_file(write_file,files_path):#输入写入文件地址和合并的文件地址列表
        with open(write_file,"ab+") as f:
            for i in files_path:
                with open(i,"rb") as f1:
                    f.write(f1.read())

    @staticmethod
    def _get_folder(data_spider,match_str = "\d([^-\d]+?)\d+$"):#区分不同爬取各步骤的文件夹返回defaultdict
        sort_dict = defaultdict(list)
        for i in os.listdir(data_spider):
            match = re.search(match_str,i)
            if match:
                sort_name = match.group(1)
                sort_dict[sort_name].append(data_spider/i)
        return sort_dict

    @staticmethod
    def _folder_tofile(folder_list,match_str = r"_ok.txt"):#文件夹到文件地址当层
        file_list = []
        for folder in folder_list:
            for file in os.listdir(folder):
                match = re.search(match_str,file)
                if match:
                    file_list.append(folder/file)
        return file_list

    @staticmethod
    def _zip7(files_names,delete=True,youxiao = ".txt"):#传入文件位置列表，进行压缩
        os.chdir(r"C:\Program Files\7-Zip")  # 修改为7-Zip目录
        for file_name in files_names:
            file_name= str(file_name)
            if youxiao in file_name:
                try:
                    print("正在压缩", file_name)
                    new_ys = re.sub("\.[^\.]*$", "压缩.7z",file_name)
                    if os.path.exists(new_ys):
                        os.remove(new_ys)
                    cmd = "7z.exe a -tzip {} {}".format(new_ys, file_name)
                    a = os.popen(cmd)
                    console_str = a.read()
                    if "Ok" in console_str:
                        print("ok")
                        if delete:
                            os.remove(file_name)
                except Exception as e:
                    print(file_name, e)

if __name__=="__main__":
    # a = SpiderFileMerge("W:\scrapy_xc")
    # while True:
    #     result = a.compression()
    #     print("----------一轮扫描压缩结束---------------")
    #     if not result:
    #         time.sleep(600)
    a = SpiderFileMerge("W:\scrapy_xc")
    finish_list = [
        # "jd_id",
        # "shopee_good",
        # "newegg_goods",
        # "taobao_look",
        # "alibabagj_shop",
        # "amazon_shopgoods",
        "smt_comment"
    ]
    a.finish(finish_list)

