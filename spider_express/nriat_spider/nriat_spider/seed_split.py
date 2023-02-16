import os
from pathlib import Path
class file_split():
    split_num = 100000#默认分割设置为100000行
    def __init__(self,file,path=r"W:\spider_seed"):#修改为项目的默认地址
        self.path = path
        self.file = file
        self.file_path = Path(self.path)/self.file
        self.file_name = self.file.split(".")[0]
        self.path_split = Path(self.path) / (self.file_name + "_split")
        self.clear_num = 0

    def change_num(self,num):
        self.split_num = num

    def split(self):
        if os.path.exists(self.file_path):
            if not os.path.exists(self.path_split):
                os.mkdir(self.path_split)
                with open(self.file_path,"r",encoding="utf-8") as f:
                    num = 0
                    str_list = []
                    file_num = 0
                    for i in f:
                        if num < self.split_num:
                            str_list.append(i)
                            num += 1
                        else:
                            with open(self.path_split / "{}_{}-{}.txt".format(self.file_name, file_num*self.split_num+1, (file_num+1)*self.split_num), "w", encoding="utf-8") as f_w:
                                f_w.writelines(str_list)
                            file_num +=1
                            str_list.clear()
                            str_list.append(i)
                            num=1
                    else:
                        if str_list:
                            with open(self.path_split / "{}_{}-{}.txt".format(self.file_name, file_num * self.split_num + 1,
                                                                     file_num * self.split_num+len(str_list)), "w",
                                      encoding="utf-8") as f_w:
                                f_w.writelines(str_list)
                                del str_list
                return True
            else:
                print("split文件夹已存在")#先不清理
                # if self.clear_num < 3:
                #     self.clear_num += 1
                #     print("清理之前存在的文件夹")
                #     self.clear_folder(self.path_split)
                #     print("第{}次重试生成文件".format(self.clear_num))
                #     return self.split()
                # else:
                #     print()
        else:
            print("种子文件不存在")

    def check(self):
        pass
    def clear_folder(self,path_split):
        if os.path.exists(path_split):
            for i in os.listdir(path_split):
                i = os.path.join(path_split,i)
                if os.path.isfile(i):
                    os.remove(i)
                else:
                    self.clear_folder(i)
                    os.removedirs(i)
            os.removedirs(path_split)

if __name__=="__main__":
    spl_c = file_split("{2_1有效店铺}[KEY].txt",r"D:\spider_seed")
    spl_c.change_num(10000)
    status = spl_c.split()
    print(status)
