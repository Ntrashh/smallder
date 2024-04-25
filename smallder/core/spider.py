from loguru import logger
from smallder import Request
from smallder.core.connection import from_redis_setting, from_mysql_setting
from smallder.core.engine import Engine


class Spider:
    name = "base"
    fastapi = True  # 控制内部统计api的数据
    server = None  # redis连接server
    mysql_server = None
    redis_url = ""  # redis连接信息
    batch_size = 0  # 批次从redis中获取多少数据
    redis_task_key = ""
    start_urls = []
    log = logger
    thread_count = 0  # 线程总数
    retry: int = 3  # 重试次数
    custom_settings = {
        "middleware_settings": {
            # "middleware.xxxx.xxx.xxxx": 100,
            # "middleware.xxxx.xxxx.xxxxxx": 500,
        },
        "dupfilter_class": "",  # "dupfilter.xxxxx.xxxxxx",
        "scheduler_class": "",  # "scheduler.xxxxx.xxxxxx"
        "mysql": "",  # "mysql://xxx:xxxxx@host:port/db_name"
    }  # 定制配置


    def setup_server(self):
        self.setup_redis()
        self.setup_mysql()

    def setup_redis(self):
        if self.server is not None:
            return
        if not (
                self.redis_url.startswith("redis://")
                or self.redis_url.startswith("rediss://")
                or self.redis_url.startswith("unix://")
        ):
            return
        self.server = from_redis_setting(self.redis_url)

    def setup_mysql(self):
        db_url = self.custom_settings.get("mysql", "")
        if not db_url:
            return
        self.mysql_server = from_mysql_setting(db_url)

    def start_request(self):
        if not len(self.start_urls):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            yield Request(url=url)

    def make_request_for_redis(self, data):
        pass

    def download_middleware(self, request):
        pass

    def parse(self, response):
        pass

    def pipline(self, item):
        pass

    def error_callback(self, failure):
        return failure.exception

    @classmethod
    def start(cls, **kwargs):
        with Engine(cls, **kwargs) as engine:
            engine.engine()

    @classmethod
    def debug(cls, **kwargs):
        with Engine(cls, **kwargs) as engine:
            spider = engine.debug()
            return spider
