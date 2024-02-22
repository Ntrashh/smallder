import _queue
import json
import queue
import traceback
from collections.abc import Iterable
from smallder import Request
from smallder.core.dupefilter import Filter, FilterFactory


class Scheduler:
    queue = queue.Queue()

    def __init__(self, dupe_filter: Filter):
        self.dupe_filter = dupe_filter

    def next_job(self, block=False):
        pass

    def add_job(self, job, block=True):
        pass

    def size(self):
        pass

    def empty(self):
        pass

    def filter_request(self, job):
        if isinstance(job, Request) and not job.dont_filter:
            return self.dupe_filter.request_seen(job)
        return False


class MemoryScheduler(Scheduler):

    def next_job(self, block=False):
        try:
            job = self.queue.get(block=block)
            if not self.filter_request(job):
                return job
        except _queue.Empty:
            pass
        except Exception:
            traceback.print_exc()

    def add_job(self, job, block=True):
        self.queue.put(job, block=block)

    def size(self):
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty()


class RedisScheduler(Scheduler):

    def __init__(self, spider, dupe_filter: Filter):
        super().__init__(dupe_filter)
        self.spider = spider
        self.server = spider.server
        # self.request_key = f"smallder:{self.spider.name}:request"
        self.request_key = f"{self.spider.redis_task_key}:request"
        self.batch_size = self.spider.batch_size or 10

    def _dict_to_request(self, d):
        if d.get("callback") is None:
            return d
        d["callback"] = getattr(self.spider, d["callback"])
        return Request(**d)

    def pop_redis_to_queue(self, redis_key):
        datas = self.pop_list_queue(redis_key, self.batch_size)
        for byte_data in datas:
            data = json.loads(byte_data.decode(), object_hook=self._dict_to_request)
            self.queue.put(data)

    def next_job(self, block=False):
        try:
            if self.queue.empty():
                self.pop_redis_to_queue(self.request_key)
            job = self.queue.get(block=block)
            if not (self.spider.skip_duplicates and self.filter_request(job)):
                return job
        except _queue.Empty:
            pass
        except Exception:
            traceback.print_exc()

    def add_job(self, job, block=True):
        if isinstance(job, Request):
            try:
                # self.spider.log.info(job)
                _str = json.dumps(job.to_dict(self.spider))
                self.server.rpush(self.request_key, _str.encode())
            except Exception as e:
                print(e)
        else:
            self.queue.put(job)
        # self.queue.put(job,block=True)

    def pop_list_queue(self, redis_key, batch_size):
        with self.server.pipeline() as pipe:
            pipe.lrange(redis_key, 0, batch_size - 1)
            pipe.ltrim(redis_key, batch_size, -1)
            datas, _ = pipe.execute()
        return datas

    def size(self):
        if self.queue.empty():
            size = self.server.llen(self.request_key) + self.queue.qsize()
        else:
            size = self.queue.qsize()
        return size

    def empty(self):
        return self.queue.empty() and not bool(self.server.llen(self.request_key))


class RedisStartScheduler(RedisScheduler):

    def next_job(self, block=False):
        try:
            found = 0
            if self.queue.empty():
                # redis 任务key不为空
                if not self.server.llen(self.request_key):
                    datas = self.pop_list_queue(self.spider.redis_task_key, self.batch_size)
                    for data in datas:
                        reqs = self.spider.make_request_for_redis(data)
                        if isinstance(reqs, Iterable):
                            for req in reqs:
                                self.queue.put(req, block=True)
                                found += 1
                        elif reqs:
                            self.queue.put(reqs, block=True)
                            found += 1
                        else:
                            print(f"Request not made from data: {data}")
                else:
                    self.pop_redis_to_queue(self.request_key)
            if found:
                self.spider.log.info(f"Read {found} requests from '{self.spider.redis_task_key}'")
            job = self.queue.get_nowait()
            if not (self.spider.skip_duplicates and self.filter_request(job)):
                return job
        except _queue.Empty:
            pass
        except Exception:
            traceback.print_exc()

    def size(self):
        if self.queue.empty():
            size = self.server.llen(self.request_key) + self.queue.qsize() + self.server.llen(
                self.spider.redis_task_key)
        else:
            size = self.queue.qsize()
        return size

    def empty(self):
        if self.queue.empty():
            return not self.server.exists(self.request_key) and not self.server.exists(self.spider.redis_task_key)

        else:
            size = self.queue.qsize()
        return not size


class SchedulerFactory:
    """
    可以新增一个调度器接口，支持用户自定义去重方法
    """

    @classmethod
    def create_scheduler(cls, spider):
        dup_filter = FilterFactory().create_filter(spider)
        if spider.server is None:
            scheduler = MemoryScheduler(dup_filter)
        else:
            if spider.redis_task_key:
                scheduler = RedisStartScheduler(spider, dup_filter)
            else:
                scheduler = RedisScheduler(spider, dup_filter)
        return scheduler
