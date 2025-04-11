# Advanced Usage

This document covers advanced usage scenarios and features of the Smallder framework.

[切换到中文文档](advanced-usage_zh.md)

## Distributed Crawling with Redis

Smallder supports distributed crawling using Redis as a central task queue and duplicate filter.

### Configuration

```python
class MyDistributedSpider(Spider):
    name = "distributed_spider"
    start_urls = ["https://example.com"]

    # Redis configuration
    custom_settings = {
        "redis": "redis://username:password@localhost:6379/0"
    }
```

### Using a Redis Task Queue

You can use Redis as a source of tasks by setting the `redis_task_key` attribute:

```python
class RedisSpider(Spider):
    name = "redis_spider"
    redis_task_key = "my_spider:tasks"

    custom_settings = {
        "redis": "redis://localhost:6379/0"
    }

    def make_request_for_redis(self, data):
        # Convert Redis data to Request objects
        url = data.decode('utf-8')
        return Request(url=url, callback=self.parse)
```

## Database Integration with MySQL

Smallder can integrate with MySQL for storing crawled data.

### Configuration

```python
class DatabaseSpider(Spider):
    name = "db_spider"
    start_urls = ["https://example.com"]

    # MySQL configuration
    custom_settings = {
        "mysql": "mysql://username:password@localhost:3306/database_name"
    }

    def pipline(self, item):
        # Store item in MySQL
        if self.mysql_server:
            with self.mysql_server.connect() as connection:
                connection.execute(
                    "INSERT INTO items (url, title) VALUES (:url, :title)",
                    item
                )
```

## Batch Processing

Smallder supports batch processing of items for more efficient database operations.

```python
class BatchSpider(Spider):
    name = "batch_spider"
    start_urls = ["https://example.com"]

    # Enable batch processing
    pipline_mode = "list"
    pipline_batch = 100  # Process items in batches of 100

    def pipline(self, items):
        # Process a batch of items
        if not items:
            return

        if self.mysql_server:
            with self.mysql_server.connect() as connection:
                connection.execute(
                    "INSERT INTO items (url, title) VALUES (:url, :title)",
                    items
                )
```

## Custom Middleware

You can create custom middleware to process requests and responses.

```python
# middleware/custom.py
class CustomMiddleware:
    def __init__(self, spider):
        self.spider = spider

    def process_request(self, request):
        # Add custom headers
        request.headers["X-Custom"] = "Value"
        return request

    def process_response(self, response):
        # Log response status
        self.spider.log.info(f"Response status: {response.status_code}")
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

## Custom Duplicate Filter

You can create a custom duplicate filter to control which requests are considered duplicates.

```python
# dupfilter/custom.py
from smallder.core.dupfilter import Filter

class CustomFilter(Filter):
    def __init__(self):
        self.seen_urls = set()

    def request_seen(self, request):
        # Only consider the URL path for duplicate detection
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

## Custom Scheduler

You can create a custom scheduler to control how requests are queued and prioritized.

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
        # Higher priority requests are processed first
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
        # High priority request
        yield Request(
            url="https://example.com/important",
            callback=self.parse_important,
            priority=1
        )

        # Normal priority request
        yield Request(
            url="https://example.com/normal",
            callback=self.parse_normal,
            priority=0
        )
```

## Custom Request and Response Handling

### Custom Request Fetching

You can provide a custom fetch method for specific requests:

```python
def custom_fetch(request):
    # Custom fetch logic
    return Response(
        url=request.url,
        status_code=200,
        content=b"Custom response content",
        request=request
    )

def parse(self, response):
    yield Request(
        url="https://example.com/custom",
        callback=self.parse_custom,
        fetch=custom_fetch
    )
```

### Request from cURL

You can create requests from cURL commands:

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

## Signal System

Smallder provides a signal system for hooking into various events:

```python
class SignalSpider(Spider):
    name = "signal_spider"
    start_urls = ["https://example.com"]

    def __init__(self):
        # Register custom signal handler
        self.signal_manager.connect("SPIDER_STATS", self.handle_stats)

    def handle_stats(self, **kwargs):
        self.log.info(f"Stats update: {kwargs}")
```

## Monitoring with FastAPI

Smallder includes a built-in monitoring API powered by FastAPI:

```python
class MonitoredSpider(Spider):
    name = "monitored_spider"
    start_urls = ["https://example.com"]

    # Enable FastAPI monitoring (enabled by default)
    fastapi = True
```

When the spider is running, you can access the monitoring API at http://localhost:8000 to see real-time statistics.

## Error Handling and Retries

### Custom Error Handling

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
        self.log.error(f"Request failed: {failure.request.url}")
        self.log.error(f"Exception: {failure.exception}")

        # You can yield a new request or item here
        yield Request(
            url="https://example.com/backup",
            callback=self.parse
        )

    def error_callback(self, failure):
        # Global error handler for all requests without specific errbacks
        self.log.error(f"Global error handler: {failure.exception}")
        return failure.exception
```

### Controlling Retries

```python
from smallder.core.error import RetryException, DiscardException

class RetrySpider(Spider):
    name = "retry_spider"
    start_urls = ["https://example.com"]
    max_retry = 5  # Maximum retry attempts

    def parse(self, response):
        if response.status_code == 429:  # Too Many Requests
            # Force a retry
            raise RetryException("Rate limited, retrying...")

        if response.status_code == 404:
            # Don't retry this request
            raise DiscardException("Page not found, skipping...")

        # Process successful response
        yield {"url": response.url, "status": "success"}
```
