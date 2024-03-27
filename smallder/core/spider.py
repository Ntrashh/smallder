from loguru import logger

from smallder import Request
from smallder.core.connection import from_setting
from smallder.core.engine import Engine


class Spider:
    name = "base"
    fastapi = True  # 控制内部统计api的数据
    server = None  # redis连接server
    redis_url = ""  # redis连接信息
    batch_size = 0  # 批次从redis中获取多少数据
    redis_task_key = ""
    start_urls = []
    log = logger
    thread_count = 0
    retry = 3
    custom_settings = {}

    def setup_redis(self):
        if self.server is not None:
            return
        if not (
                self.redis_url.startswith("redis://")
                or self.redis_url.startswith("rediss://")
                or self.redis_url.startswith("unix://")
        ):
            return
        self.server = from_setting(self.redis_url)

    def start_request(self):
        if not len(self.start_urls):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            yield Request(url, dont_filter=True)

    def make_request_for_redis(self, data):
        pass

    def download_middleware(self, request):
        pass

    def parse(self, response):
        pass

    def pipline(self, item):
        pass

    @classmethod
    def start(cls, **kwargs):
        with Engine(cls, **kwargs) as engine:
            engine.engine()

    @classmethod
    def debug(cls, **kwargs):
        with Engine(cls, **kwargs) as engine:
            spider = engine.debug()
            return spider
