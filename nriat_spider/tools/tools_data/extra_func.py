import time
from functools import wraps

def run_time(func):
    @wraps(func)
    def use_time(*args,**kwargs):
        a = lambda :time.time()
        start_time = a()
        func(*args,**kwargs)
        end_time = a()
        print(end_time-start_time)
    return use_time