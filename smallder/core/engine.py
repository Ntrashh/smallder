import json
import os
import queue
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from requests import RequestException
from smallder.api.app import FastAPIWrapper
from smallder.core.downloader import Downloader
from smallder.core.failure import Failure
from smallder.core.item import Item
from smallder.core.middleware import MiddlewareManager
from smallder.core.scheduler import SchedulerFactory
from smallder.core.statscollectors import MemoryStatsCollector
from typing_extensions import Dict


class Engine:
    stats = MemoryStatsCollector()
    fastapi_manager = FastAPIWrapper()
    item_que = queue.Queue()
    futures = deque()

    def __init__(self, spider, **kwargs):
        self.spider = spider(**kwargs)
        self.spider.setup_server()
        self.download = Downloader(self.spider)
        self.middleware_manager = MiddlewareManager(self.spider)
        self.scheduler = SchedulerFactory.create_scheduler(self.spider)
        self.default_thread_count = self.spider.thread_count if self.spider.thread_count else os.cpu_count() * 2
        self.start_requests = iter(self.spider.start_request())
        self.setup_signals()

    def setup_signals(self):
        # 在这里注册爬虫开始
        self.spider.connect_start_signal(self.middleware_manager.load_middlewares)
        self.spider.connect_start_signal(self.spider.setup)
        self.spider.connect_start_signal(self.stats.on_spider_start)
        if self.spider.fastapi:
            self.spider.connect_start_signal(self.fastapi_manager.run)
        # 在这里注册爬虫结束的信号
        self.spider.connect_stop_signal(self.stats.on_spider_stopped)

    def future_done(self, future):
        try:
            self.futures.remove(future)
        except ValueError as e:
            self.spider.log.warning(e)  # Future 已经被移除

    @stats.handler
    def process_request(self, request=None):
        try:
            middleware_manager_request = self.middleware_manager.process_request(request)
            download_middleware_request = self.spider.download_middleware(middleware_manager_request)
            if download_middleware_request is not None:
                middleware_manager_request = download_middleware_request
            response = self.download.download(middleware_manager_request)
            self.spider.log.info(response)
            self.scheduler.add_job(response)
        except Exception as e:
            process_error = self.process_callback_error(e=e, request=request)
            if not isinstance(process_error, BaseException):
                raise Exception("err_callback function must return Exception")
            self.spider.log.exception(process_error)
            # 这里还是要处理重试的问题
            if isinstance(e, RequestException):
                # 如果是request引发的问题就需要处理
                if request.retry + 1 < self.spider.max_retry:
                    request.retry += 1
                    request.dont_filter = True
                    self.scheduler.add_job(request)
                else:
                    fail_request = request.replace(retry=0, dont_filter=False)
                    self.scheduler.add_failed_job(job=fail_request)
                self.spider.log.info(
                    f"""
                    request : {request}
                    重试次数 : {request.retry}
                    最大允许重试次数 : {self.spider.max_retry}"""
                )

    @stats.handler
    def process_response(self, response=None):
        try:
            response = self.middleware_manager.process_response(response)
            callback = response.request.callback or getattr(self.spider, "error_callback", None)
            _iters = callback(response)
            if _iters is None:
                return
            for _iter in _iters:
                self.scheduler.add_job(_iter, block=False)
        except Exception as e:
            process_error = self.process_callback_error(e=e, request=response.request, response=response)
            if isinstance(process_error, BaseException):
                self.spider.log.exception(process_error)

    @stats.handler
    def process_item(self, item: [Item, Dict, None]):
        try:
            if self.spider.pipline_mode == "single":
                self.spider.pipline(item)
            else:
                if self.item_que.qsize() > self.spider.pipline_batch or item is None:
                    items = []
                    while self.item_que.empty():
                        items.append(self.item_que.get())
                    self.spider.pipline(items)
                if item is not None:
                    self.item_que.put(item)
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
            else:
                self.process_item(item=None)

        self.spider.log.info(f"任务池数量:{len(self.futures)},redis中任务是否为空:{self.scheduler.empty()} ")

    def debug(self):
        rounds = 0
        while rounds < 6:
            try:
                if self.scheduler.empty() and self.start_requests is None:
                    time.sleep(0.2)
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
        else:
            self.process_item(item=None)
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
        request_err_back = request.errback or getattr(self.spider, "error_callback", None)
        failure = Failure(exception=e, request=request, response=response)
        return request_err_back(failure)

    def __enter__(self):
        self.spider.signal_manager.send("SPIDER_STARTED")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spider.log.info(
            f"exc_type :{exc_type} exc_val :{exc_val} 任务池数量:{len(self.futures)},任务队列是否为空:{self.scheduler.empty()} ")
        if exc_tb:
            self.spider.log.warning(traceback.format_exc(exc_tb))
        self.spider.signal_manager.send("SPIDER_STOPPED")
        self.spider.log.success(f"Spider Close : {json.dumps(self.stats.get_stats(), ensure_ascii=False, indent=4)}")
