import _queue
import importlib
import json
import queue
import traceback
from collections.abc import Iterable
from smallder import Request
from smallder.core.dupfilter import Filter, FilterFactory
from smallder.utils.request import request_from_dict


class Scheduler:
    queue = queue.Queue()

    def __init__(self, spider, dup_filter: Filter):
        self.spider = spider
        self.batch_size = self.spider.batch_size or self.spider.thread_count * 10
        self.dup_filter = dup_filter

    def next_job(self, block=False):
        pass

    def add_job(self, job, block=False):
        pass

    def size(self):
        pass

    def empty(self):
        pass

    def add_failed_job(self, job, block=False):
        pass

    def filter_request(self, job):
        """
        过滤任务，如果是request并且需要去重就进行过滤
        :param job:
        :return:
        """
        if isinstance(job, Request) and not job.dont_filter:
            return not self.dup_filter.request_seen(job)
        return True

    def __repr__(self):
        return f"<Scheduler with {self.size()} tasks>"


class MemoryScheduler(Scheduler):

    def next_job(self, block=False):
        try:
            job = self.queue.get(block=block)
            if self.filter_request(job):
                return job
        except _queue.Empty:
            pass
        except Exception:
            traceback.print_exc()

    def add_job(self, job, block=False):
        self.queue.put(job, block=block)

    def size(self):
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty()


class RedisScheduler(Scheduler):

    def __init__(self, spider, dup_filter: Filter):
        super().__init__(spider, dup_filter)
        self.spider = spider
        self.server = spider.server
        self.request_key = self.spider.redis_task_key if self.spider.redis_task_key else f"{self.spider.name}:request"
        self.fail_request_key = f"{self.spider.redis_task_key}:fail_request" \
            if self.spider.redis_task_key else f"{self.spider.name}:fail_request"

    def _request_from_dict(self, d):
        return request_from_dict(d, self.spider)

    def pop_redis_to_queue(self, redis_key):
        datas = self.pop_list_queue(redis_key, self.batch_size)
        for byte_data in datas:
            data = self._request_from_dict(json.loads(byte_data.decode()))
            self.queue.put(data)

    def next_job(self, block=False):
        try:
            if self.queue.empty():
                self.pop_redis_to_queue(self.request_key)
            job = self.queue.get(block=block)
            if self.filter_request(job):
                return job
        except _queue.Empty:
            pass
        except Exception as e:
            self.spider.log.exception(e)

    def add_job(self, job, block=False):
        if isinstance(job, Request):
            try:
                _str = json.dumps(job.to_dict(self.spider))
                self.server.rpush(self.request_key, _str.encode())
            except Exception as e:
                self.spider.log.exception(e)
        else:
            self.queue.put(job)

    def add_failed_job(self, job, block=False):
        if isinstance(job, Request) and self.spider.save_failed_request:
            try:
                _str = json.dumps(job.to_dict(self.spider))
                self.server.rpush(self.fail_request_key, _str.encode())
            except Exception as e:
                self.spider.log.exception(e)

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
                                self.queue.put(req, block=block)
                                found += 1
                        elif reqs:
                            self.queue.put(reqs, block=block)
                            found += 1
                        else:
                            print(f"Request not made from data: {data}")
                else:
                    self.pop_redis_to_queue(self.request_key)
            if found:
                self.spider.log.info(f"Read {found} requests from '{self.spider.redis_task_key}'")
            job = self.queue.get_nowait()
            if self.filter_request(job):
                return job
        except _queue.Empty:
            pass
        except Exception as e:
            self.spider.log.exception(e)

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
        dup_filter = FilterFactory.create_filter(spider)
        _scheduler_cls = cls.load_filter(spider)
        if _scheduler_cls is not None:
            instance = _scheduler_cls(spider, dup_filter)
            return instance
        if spider.server is None:
            scheduler = MemoryScheduler(spider, dup_filter)
        else:
            if spider.redis_task_key:
                scheduler = RedisStartScheduler(spider, dup_filter)
            else:
                scheduler = RedisScheduler(spider, dup_filter)
        return scheduler

    @classmethod
    def load_filter(cls, spider):
        mw_path = spider.custom_settings.get("scheduler_class", "")
        if not mw_path:
            return
        try:
            if not mw_path:
                return
            module_path, class_name = mw_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            spider.log.error(f"Failed to load middleware class {mw_path}: {e}")
            return None
