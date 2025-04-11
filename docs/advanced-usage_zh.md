# 高级用法

本文档涵盖了 Smallder 框架的高级用法场景和功能。

## 使用 Redis 进行分布式爬取

Smallder 支持使用 Redis 作为中央任务队列和重复过滤器进行分布式爬取。

### 配置

```python
class MyDistributedSpider(Spider):
    name = "distributed_spider"
    start_urls = ["https://example.com"]
    
    # Redis 配置
    custom_settings = {
        "redis": "redis://username:password@localhost:6379/0"
    }
```

### 使用 Redis 任务队列

您可以通过设置 `redis_task_key` 属性使用 Redis 作为任务源：

```python
class RedisSpider(Spider):
    name = "redis_spider"
    redis_task_key = "my_spider:tasks"
    
    custom_settings = {
        "redis": "redis://localhost:6379/0"
    }
    
    def make_request_for_redis(self, data):
        # 将 Redis 数据转换为 Request 对象
        url = data.decode('utf-8')
        return Request(url=url, callback=self.parse)
```

## 与 MySQL 集成

Smallder 可以与 MySQL 集成以存储爬取的数据。

### 配置

```python
class DatabaseSpider(Spider):
    name = "db_spider"
    start_urls = ["https://example.com"]
    
    # MySQL 配置
    custom_settings = {
        "mysql": "mysql://username:password@localhost:3306/database_name"
    }
    
    def pipline(self, item):
        # 将项目存储在 MySQL 中
        if self.mysql_server:
            with self.mysql_server.connect() as connection:
                connection.execute(
                    "INSERT INTO items (url, title) VALUES (:url, :title)",
                    item
                )
```

## 批处理

Smallder 支持项目批处理，以实现更高效的数据库操作。

```python
class BatchSpider(Spider):
    name = "batch_spider"
    start_urls = ["https://example.com"]
    
    # 启用批处理
    pipline_mode = "list"
    pipline_batch = 100  # 每批处理 100 个项目
    
    def pipline(self, items):
        # 处理一批项目
        if not items:
            return
            
        if self.mysql_server:
            with self.mysql_server.connect() as connection:
                connection.execute(
                    "INSERT INTO items (url, title) VALUES (:url, :title)",
                    items
                )
```

## 自定义中间件

您可以创建自定义中间件来处理请求和响应。

```python
# middleware/custom.py
class CustomMiddleware:
    def __init__(self, spider):
        self.spider = spider
    
    def process_request(self, request):
        # 添加自定义头
        request.headers["X-Custom"] = "Value"
        return request
    
    def process_response(self, response):
        # 记录响应状态
        self.spider.log.info(f"响应状态: {response.status_code}")
        return response

# spider.py
class MiddlewareSpider(Spider):
    name = "middleware_spider"
    start_urls = ["https://example.com"]
    
    custom_settings = {
        "middleware_settings": {
            "middleware.custom.CustomMiddleware": 100,
        }
    }
```

## 自定义重复过滤器

您可以创建自定义重复过滤器来控制哪些请求被视为重复。

```python
# dupfilter/custom.py
from smallder.core.dupfilter import Filter

class CustomFilter(Filter):
    def __init__(self):
        self.seen_urls = set()
    
    def request_seen(self, request):
        # 仅考虑 URL 路径进行重复检测
        from urllib.parse import urlparse
        url_path = urlparse(request.url).path
        
        if url_path in self.seen_urls:
            return True
        
        self.seen_urls.add(url_path)
        return False

# spider.py
class CustomFilterSpider(Spider):
    name = "custom_filter_spider"
    start_urls = ["https://example.com"]
    
    custom_settings = {
        "dupfilter_class": "dupfilter.custom.CustomFilter",
    }
```

## 自定义调度器

您可以创建自定义调度器来控制请求的队列和优先级。

```python
# scheduler/custom.py
from smallder.core.scheduler import Scheduler
import queue

class PriorityScheduler(Scheduler):
    def __init__(self, spider, dup_filter):
        super().__init__(spider, dup_filter)
        self.queue = queue.PriorityQueue()
    
    def next_job(self, block=False):
        try:
            _, job = self.queue.get(block=block)
            if self.filter_request(job):
                return job
        except queue.Empty:
            pass
    
    def add_job(self, job, block=False):
        # 优先级高的请求先处理
        priority = getattr(job, 'priority', 0)
        self.queue.put((priority, job), block=block)
    
    def size(self):
        return self.queue.qsize()
    
    def empty(self):
        return self.queue.empty()

# spider.py
class PrioritySpider(Spider):
    name = "priority_spider"
    start_urls = ["https://example.com"]
    
    custom_settings = {
        "scheduler_class": "scheduler.custom.PriorityScheduler",
    }
    
    def parse(self, response):
        # 高优先级请求
        yield Request(
            url="https://example.com/important",
            callback=self.parse_important,
            priority=1
        )
        
        # 普通优先级请求
        yield Request(
            url="https://example.com/normal",
            callback=self.parse_normal,
            priority=0
        )
```

## 自定义请求和响应处理

### 自定义请求获取

您可以为特定请求提供自定义获取方法：

```python
def custom_fetch(request):
    # 自定义获取逻辑
    return Response(
        url=request.url,
        status_code=200,
        content=b"自定义响应内容",
        request=request
    )

def parse(self, response):
    yield Request(
        url="https://example.com/custom",
        callback=self.parse_custom,
        fetch=custom_fetch
    )
```

### 从 cURL 创建请求

您可以从 cURL 命令创建请求：

```python
def start_requests(self):
    curl_cmd = """
    curl 'https://example.com/api' \
      -H 'User-Agent: Mozilla/5.0' \
      -H 'Accept: application/json' \
      --data-raw '{"query":"test"}'
    """
    
    yield Request.from_curl(curl_cmd, callback=self.parse_api)
```

## 信号系统

Smallder 提供了一个信号系统，用于挂钩各种事件：

```python
class SignalSpider(Spider):
    name = "signal_spider"
    start_urls = ["https://example.com"]
    
    def __init__(self):
        # 注册自定义信号处理程序
        self.signal_manager.connect("SPIDER_STATS", self.handle_stats)
    
    def handle_stats(self, **kwargs):
        self.log.info(f"统计更新: {kwargs}")
```

## 使用 FastAPI 进行监控

Smallder 包含一个由 FastAPI 提供支持的内置监控 API：

```python
class MonitoredSpider(Spider):
    name = "monitored_spider"
    start_urls = ["https://example.com"]
    
    # 启用 FastAPI 监控（默认启用）
    fastapi = True
```

当爬虫运行时，您可以访问 http://localhost:8000 查看实时统计信息。

## 错误处理和重试

### 自定义错误处理

```python
class ErrorHandlingSpider(Spider):
    name = "error_spider"
    start_urls = ["https://example.com"]
    
    def start_requests(self):
        yield Request(
            url="https://example.com/might-fail",
            callback=self.parse,
            errback=self.handle_error
        )
    
    def handle_error(self, failure):
        self.log.error(f"请求失败: {failure.request.url}")
        self.log.error(f"异常: {failure.exception}")
        
        # 您可以在这里生成新的请求或项目
        yield Request(
            url="https://example.com/backup",
            callback=self.parse
        )
    
    def error_callback(self, failure):
        # 所有没有特定 errback 的请求的全局错误处理程序
        self.log.error(f"全局错误处理程序: {failure.exception}")
        return failure.exception
```

### 控制重试

```python
from smallder.core.error import RetryException, DiscardException

class RetrySpider(Spider):
    name = "retry_spider"
    start_urls = ["https://example.com"]
    max_retry = 5  # 最大重试次数
    
    def parse(self, response):
        if response.status_code == 429:  # 请求过多
            # 强制重试
            raise RetryException("速率限制，正在重试...")
        
        if response.status_code == 404:
            # 不重试此请求
            raise DiscardException("页面未找到，跳过...")
            
        # 处理成功的响应
        yield {"url": response.url, "status": "success"}
```

---

[切换到英文文档](advanced-usage.md)
