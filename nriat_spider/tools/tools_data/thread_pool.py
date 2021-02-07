from threading import Thread
import time
from tools.tools_data.extra_func import run_time
from threading import Lock
from queue import Queue


class MyThread(Thread):
    def __init__(self, thread_id,q,lock,group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,args=args, kwargs=kwargs,daemon=daemon)
        self.thread_id = thread_id
        self.lock = lock
        self.exit_flag = 0
        self.q = q

    def run(self):
        print("开启线程：{}".format(self.thread_id))
        self.process_data(self.thread_id)#循环使用
        print("退出线程：{}".format(self.thread_id))

    def process_data(self,thread_id):
        while not self.exit_flag:
            self.lock.acquire()
            if not self.q.empty():
                func,args,kwargs = self.q.get()
                self.lock.release()
                func(thread_id,*args,**kwargs)
                # 数据处理
                # print("processing {}".format(threadID))
            else:
                self.lock.release()

    def change_exitflag(self):
        self.exit_flag = 1


class ThreaPool(object):
    def __init__(self):
        # 线程的参数
        self.work_queue = Queue()
        self.queue_lock = Lock()
        self.thread_id = 1
        self.threads = []

    def data_queue(self):
        raise NotImplementedError

    @run_time
    def thread_pool(self, size=10):
        for i in range(size):
            thread = MyThread(self.thread_id, self.work_queue, self.queue_lock)
            thread.start()
            self.threads.append(thread)
            self.thread_id += 1
        # 填充队列
        self.queue_lock.acquire()
        self.data_queue()
        self.queue_lock.release()
        # 等待队列清空
        while not self.work_queue.empty():
            print("队列没有空")
            time.sleep(0.5)
            pass
        # 通知线程是时候退出
        for i in self.threads:
            i.change_exitflag()
        # 等待所有线程完成
        for t in self.threads:
            t.join()
        print("退出主线程")