import time
import random

class format_string():
    def date_num(self,last_num=random.randint(1,999)):
        last_num = last_num % 10000
        date_format = time.strftime("%Y%m%d%H%M%S", time.localtime())
        num = str(int(date_format) * 10000 + last_num)
        return num
    def year_second(self):
        date_format = time.strftime("%Y%m%d%H%M%S", time.localtime())
        return date_format

if __name__=="__main__":
    print(format_string().date_num())
