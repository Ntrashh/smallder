import json
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from smallder.api.app import FastAPIWrapper
from smallder.core.customsignalmanager import CustomSignalManager
from smallder.core.downloader import Downloader
from smallder.core.failure import Failure
from smallder.core.item import Item
from smallder.core.middleware import MiddlewareManager
from smallder.core.scheduler import SchedulerFactory
from smallder.core.statscollectors import MemoryStatsCollector


class Engine:
    stats = MemoryStatsCollector()
    signal_manager = CustomSignalManager()
    fastapi_manager = FastAPIWrapper()
    futures = deque()

    def __init__(self, spider, **kwargs):
        self.spider = spider(**kwargs)
        self.download = Downloader(self.spider)
        self.middleware_manager = MiddlewareManager(self.spider)
        self.start_requests = iter(self.spider.start_request())
        self.setup_signals()
        self.spider.setup_redis()
        self.scheduler = SchedulerFactory.create_scheduler(self.spider)
        self.default_thread_count = self.spider.thread_count if self.spider.thread_count else os.cpu_count() * 2

    def setup_signals(self):
        # 在这里注册爬虫开始和结束的信号
        self.signal_manager.connect("SPIDER_STOPPED", self.stats.on_spider_stopped)
        self.signal_manager.connect("SPIDER_STARTED", self.middleware_manager.load_middlewares)
        if self.spider.fastapi:
            self.signal_manager.connect("SPIDER_STARTED", self.fastapi_manager.run)

    def future_done(self, future):
        try:
            self.futures.remove(future)
        except ValueError as e:
            self.spider.log.warning(e)  # Future 已经被移除

    @stats.handler
    def process_request(self, request=None):
        try:
            middleware_request = self.spider.download_middleware(request)
            if middleware_request is not None:
                request = middleware_request
            middleware_manager = self.middleware_manager.process_request(request)
            response = self.download.download(middleware_manager)
            self.spider.log.info(response)
            self.scheduler.add_job(response)
        except Exception as e:
            process_error = self.process_callback_error(e=e, request=request)
            if isinstance(process_error, BaseException):
                self.spider.log.exception(process_error)

    @stats.handler
    def process_response(self, response=None):
        try:
            response = self.middleware_manager.process_response(response)
            callback = response.request.callback or getattr(self.spider, "parse", None)
            _iters = callback(response)
            if _iters is None:
                return
            for _iter in _iters:
                self.scheduler.add_job(_iter, block=True)
        except Exception as e:
            process_error = self.process_callback_error(e=e, request=response.request, response=response)
            if isinstance(process_error, BaseException):
                self.spider.log.exception(process_error)

    @stats.handler
    def process_item(self, item=Item):
        try:
            self.spider.pipline(item)
        except Exception as e:
            self.spider.log.exception(f"{item} 入库出现错误 \n {e}")

    def engine(self):
        rounds = 0
        with ThreadPoolExecutor(max_workers=self.default_thread_count) as executor:
            end = 600 if self.spider.server else 10
            while rounds < end:
                try:
                    if len(self.futures) > self.default_thread_count * 20:
                        time.sleep(0.1)
                        continue
                    if not len(self.futures) and self.scheduler.empty() and self.start_requests is None:
                        time.sleep(0.1)
                        rounds += 1
                    if self.start_requests is not None:
                        try:
                            task = next(self.start_requests)
                            self.scheduler.add_job(task)
                        except StopIteration:
                            self.start_requests = None
                        except Exception:
                            self.start_requests = None
                    task = self.scheduler.next_job()
                    if task is None:
                        time.sleep(0.01)
                        continue
                    process_func = self.process_func(task)
                    future = executor.submit(process_func, task)
                    self.futures.append(future)
                    future.add_done_callback(self.future_done)
                    rounds = 0
                except Exception as e:
                    self.spider.log.exception(f"调度引擎出现错误 \n {e}")
        self.spider.log.info(f"任务池数量:{len(self.futures)},redis中任务是否为空:{self.scheduler.empty()} ")

    def debug(self):
        rounds = 0
        while rounds < 6:
            try:
                if len(self.futures) > self.default_thread_count * 6:
                    time.sleep(0.5)
                    continue
                if not len(self.futures) and self.scheduler.empty() and self.start_requests is None:
                    time.sleep(0.5)
                    rounds += 1
                if self.start_requests is not None:
                    try:
                        task = next(self.start_requests)
                        self.scheduler.add_job(task)
                    except StopIteration:
                        self.start_requests = None
                    except Exception:
                        self.start_requests = None
                task = self.scheduler.next_job()
                if task is None:
                    time.sleep(0.1)
                    continue
                process_func = self.process_func(task)
                process_func(task)
                rounds = 0
            except Exception as e:
                self.spider.log.exception(f"调度引擎出现错误 \n {e}")

        return self.spider

    def process_func(self, task):
        cls_name = type(task).__name__
        func_dict = {
            "Request": self.process_request,
            "Response": self.process_response,
            "dict": self.process_item,
            "Item": self.process_item,
        }
        func = func_dict.get(cls_name)
        if func is None:
            raise ValueError(f"{task} does not exist")
        return func

    def process_callback_error(self, e, request, response=None):
        request_err_back = request.errback or self.spider.error_callback
        failure = Failure(exception=e, request=request, response=response)
        return request_err_back(failure)

    def __enter__(self):
        self.signal_manager.send("SPIDER_STARTED")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spider.log.info(
            f"exc_type :{exc_type} exc_val :{exc_val} 任务池数量:{len(self.futures)},redis中任务是否为空:{self.scheduler.empty()} ")
        if exc_tb:
            self.spider.log.warning(traceback.format_exc(exc_tb))
        self.signal_manager.send("SPIDER_STOPPED")
        self.spider.log.success(f"Spider Close : {json.dumps(self.stats.get_stats(), ensure_ascii=False, indent=4)}")
