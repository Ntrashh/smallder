from loguru import logger
from smallder import Request
from smallder.core.connection import from_redis_setting, from_mysql_setting
from smallder.core.customsignalmanager import CustomSignalManager
from smallder.core.engine import Engine


class Spider:
    signal_manager = CustomSignalManager()
    name = "base"
    fastapi = True  # 控制内部统计api的数据
    server = None  # redis连接server
    mysql_server = None  # mysql链接server
    redis_url = ""  # redis连接信息
    batch_size = 0  # 批次从redis中获取多少数据
    redis_task_key = ""  # 任务池key如果存在值,则直接从redis中去任务,需要重写make_request_for_redis
    start_urls = []
    log = logger
    thread_count = 0  # 线程总数
    retry: int = 3  # 重试次数
    pipline_mode = "single"  # 两种模式 single代表单条入库,list代表多条入库
    pipline_batch = 100  # 只有在pipline_mode=list时生效,代表多少条item进入pipline,默认100
    custom_settings = {
        "middleware_settings": {
            # "middleware.xxxx.xxx.xxxx": 100,
            # "middleware.xxxx.xxxx.xxxxxx": 500,
        },
        "dupfilter_class": "",  # "dupfilter.xxxxx.xxxxxx",
        "scheduler_class": "",  # "scheduler.xxxxx.xxxxxx"
        "mysql": "",  # "mysql://xxx:xxxxx@host:port/db_name"
    }  # 定制配置

    def connect_start_signal(self, func):
        self.signal_manager.connect("SPIDER_STARTED", func)

    def connect_stop_signal(self, func):
        self.signal_manager.connect("SPIDER_STOPPED", func)

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

    def setup(self):
        """
        引擎开始启动的时候会通知到这里,这里可以做一些自定义设置
        @return:
        """
        pass

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

        """
        @param item:
        @return:
        # 插入数据
        data = [
            ('Object 1',),
            ('Object 2',),
            ('Object 3',)
        ]

        # 使用原生 SQL 进行批量插入多条数据
        with self.mysql_server.connect() as connection:
            connection.execute(
                text("INSERT INTO my_model (name) VALUES (:name)"),
                [{'name': name} for name, in data]
            )

        # 插入单条数据
        data = {'name': 'Single Object'}

        # 使用原生 SQL 插入单条数据
        with self.mysql_server.connect() as connection:
            connection.execute(
                text("INSERT INTO my_model (name) VALUES (:name)"),
                data
            )

        """
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
