# API Reference

This document provides detailed information about the classes and methods available in the Smallder framework.

[切换到中文文档](api-reference_zh.md)

## Spider

The base class for all spiders.

```python
class Spider:
    name = "base"
    fastapi = True
    server = None
    mysql_server = None
    batch_size = 0
    redis_task_key = ""
    start_urls = []
    thread_count = os.cpu_count() * 2
    max_retry = 10
    save_failed_request = False
    pipline_mode = "single"
    pipline_batch = 100
    custom_settings = {}
```

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | str | Unique identifier for the spider |
| `fastapi` | bool | Enable/disable monitoring API |
| `server` | redis.StrictRedis | Redis connection (set automatically) |
| `mysql_server` | sqlalchemy.engine.Engine | MySQL connection (set automatically) |
| `batch_size` | int | Number of tasks to fetch from Redis at once |
| `redis_task_key` | str | Redis key for task queue |
| `start_urls` | list | List of URLs to start crawling |
| `thread_count` | int | Number of concurrent threads |
| `max_retry` | int | Maximum retry attempts for failed requests |
| `save_failed_request` | bool | Save failed requests to Redis |
| `pipline_mode` | str | Item processing mode ("single" or "list") |
| `pipline_batch` | int | Batch size for list mode |
| `custom_settings` | dict | Dictionary of custom settings |

### Methods

#### `start_requests()`

Generates initial requests from `start_urls`.

**Returns**: Generator of `Request` objects

#### `parse(response)`

Default callback for processing responses.

**Parameters**:
- `response` (Response): The response to parse

**Returns**: Generator of items or `Request` objects

#### `download_middleware(request)`

Processes requests before downloading.

**Parameters**:
- `request` (Request): The request to process

**Returns**: Modified `Request` object

#### `make_request_for_redis(data)`

Converts Redis data to `Request` objects.

**Parameters**:
- `data` (bytes): Data from Redis

**Returns**: `Request` object or list of `Request` objects

#### `pipline(item)`

Processes yielded items.

**Parameters**:
- `item` (dict): Item to process (or list of items in "list" mode)

#### `on_start()`

Called when the spider starts.

#### `on_stop()`

Called when the spider stops.

#### `error_callback(failure)`

Called when an error occurs.

**Parameters**:
- `failure` (Failure): Object containing error information

**Returns**: Exception object

#### `inc_value(key_name)`

Increments a statistics counter.

**Parameters**:
- `key_name` (str): Name of the counter to increment

#### `connect_start_signal(func)`

Connects a function to the spider start signal.

**Parameters**:
- `func` (callable): Function to call when the spider starts

#### `connect_stop_signal(func)`

Connects a function to the spider stop signal.

**Parameters**:
- `func` (callable): Function to call when the spider stops

#### `setup_server()`

Sets up Redis and MySQL connections.

#### `setup_redis()`

Sets up the Redis connection.

#### `setup_mysql()`

Sets up the MySQL connection.

#### `start(**kwargs)`

Class method to start the spider.

**Parameters**:
- `**kwargs`: Keyword arguments to pass to the spider constructor

#### `debug(**kwargs)`

Class method to run the spider in debug mode.

**Parameters**:
- `**kwargs`: Keyword arguments to pass to the spider constructor

**Returns**: Spider instance

## Request

Represents an HTTP request.

```python
class Request:
    def __init__(
        self,
        method="get",
        url=None,
        headers=None,
        params=None,
        data=None,
        json=None,
        cookies=None,
        timeout=5,
        callback=None,
        errback=None,
        meta=None,
        referer=None,
        proxies=None,
        dont_filter=False,
        verify=False,
        allow_redirects=True,
        priority=0,
        fetch=None,
        retry=0
    ):
        # ...
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `method` | str | HTTP method | "get" |
| `url` | str | URL to request | None |
| `headers` | dict | HTTP headers | None |
| `params` | dict | URL parameters | None |
| `data` | dict/str | POST data | None |
| `json` | dict | JSON data | None |
| `cookies` | dict | Cookies | None |
| `timeout` | int | Request timeout in seconds | 5 |
| `callback` | callable | Function to call with the response | None |
| `errback` | callable | Function to call on error | None |
| `meta` | dict | Metadata dictionary | None |
| `referer` | str | Referer URL | None |
| `proxies` | dict | Proxy settings | None |
| `dont_filter` | bool | Skip duplicate filtering | False |
| `verify` | bool | Verify SSL certificates | False |
| `allow_redirects` | bool | Follow redirects | True |
| `priority` | int | Request priority | 0 |
| `fetch` | callable | Custom fetch function | None |
| `retry` | int | Current retry count | 0 |

### Properties

#### `meta`

Dictionary for storing metadata.

**Returns**: dict

#### `referer`

Referer URL.

**Returns**: str

#### `headers`

HTTP headers with "Connection: close" added.

**Returns**: dict

### Methods

#### `full_url()`

Returns the complete URL with parameters.

**Returns**: str

#### `copy()`

Creates a copy of the request.

**Returns**: Request

#### `replace(**kwargs)`

Creates a new request with updated attributes.

**Parameters**:
- `**kwargs`: Attributes to update

**Returns**: Request

#### `to_dict(spider)`

Converts the request to a dictionary for serialization.

**Parameters**:
- `spider` (Spider): Spider instance

**Returns**: dict

#### `from_curl(curl_command, **kwargs)`

Class method to create a request from a cURL command.

**Parameters**:
- `curl_command` (str): cURL command
- `**kwargs`: Additional parameters

**Returns**: Request

## Response

Represents an HTTP response.

```python
class Response:
    def __init__(
        self,
        url=None,
        status_code=200,
        content=None,
        request=None,
        encoding="utf-8",
        cookies=None,
        elapsed=0
    ):
        # ...
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `url` | str | URL of the response | None |
| `status_code` | int | HTTP status code | 200 |
| `content` | bytes | Raw response content | None |
| `request` | Request | Original request object | None (required) |
| `encoding` | str | Content encoding | "utf-8" |
| `cookies` | dict | Response cookies | None |
| `elapsed` | float | Time taken to receive the response | 0 |

### Properties

#### `meta`

Metadata from the original request.

**Returns**: dict

#### `referer`

Referer from the original request.

**Returns**: str

#### `text`

Decoded content as text.

**Returns**: str

#### `ok`

Whether the status code is 200.

**Returns**: bool

#### `root`

lxml HTML element for parsing.

**Returns**: lxml.html.HtmlElement

### Methods

#### `json(**kwargs)`

Parses the response as JSON.

**Parameters**:
- `**kwargs`: Arguments to pass to `json.loads()`

**Returns**: dict/list

#### `urljoin(url)`

Joins a relative URL with the response URL.

**Parameters**:
- `url` (str): Relative URL

**Returns**: str

#### `params()`

Returns the URL parameters as a dictionary.

**Returns**: dict

#### `replace(**kwargs)`

Creates a new response with updated attributes.

**Parameters**:
- `**kwargs`: Attributes to update

**Returns**: Response

## Engine

Manages the crawling process.

```python
class Engine:
    def __init__(self, spider, **kwargs):
        # ...
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `spider` | Spider class | Spider class to instantiate |
| `**kwargs` | dict | Arguments to pass to the spider constructor |

### Methods

#### `engine()`

Runs the engine in normal mode.

#### `debug()`

Runs the engine in debug mode.

**Returns**: Spider instance

#### `process_request(request)`

Processes a request.

**Parameters**:
- `request` (Request): Request to process

#### `process_response(response)`

Processes a response.

**Parameters**:
- `response` (Response): Response to process

#### `process_item(item)`

Processes an item.

**Parameters**:
- `item` (dict): Item to process

#### `handler_request_retry(request)`

Handles request retries.

**Parameters**:
- `request` (Request): Request to retry

#### `process_callback_error(e, request, response=None)`

Processes callback errors.

**Parameters**:
- `e` (Exception): Exception that occurred
- `request` (Request): Request that caused the error
- `response` (Response, optional): Response that caused the error

## Downloader

Handles HTTP requests.

```python
class Downloader:
    def __init__(self, spider):
        self.spider = spider
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `spider` | Spider | Spider instance |

### Methods

#### `fetch(request)`

Class method to fetch a response for a request.

**Parameters**:
- `request` (Request): Request to fetch

**Returns**: Response

#### `download(request)`

Downloads a response for a request, using the custom fetch method if provided.

**Parameters**:
- `request` (Request): Request to download

**Returns**: Response

## MiddlewareManager

Manages middleware components.

```python
class MiddlewareManager:
    def __init__(self, spider):
        self.spider = spider
        self.middlewares = spider.custom_settings.get("middleware_settings", {})
        self.loaded_middlewares = []
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `spider` | Spider | Spider instance |

### Methods

#### `load_middlewares()`

Loads middleware components.

#### `process_request(request)`

Processes a request through all middleware components.

**Parameters**:
- `request` (Request): Request to process

**Returns**: Modified Request

#### `process_response(response)`

Processes a response through all middleware components.

**Parameters**:
- `response` (Response): Response to process

**Returns**: Modified Response

## Scheduler

Base class for schedulers.

```python
class Scheduler:
    def __init__(self, spider, dup_filter):
        self.spider = spider
        self.batch_size = self.spider.batch_size or self.spider.thread_count * 10
        self.dup_filter = dup_filter
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `spider` | Spider | Spider instance |
| `dup_filter` | Filter | Duplicate filter instance |

### Methods

#### `next_job(block=False)`

Gets the next job from the queue.

**Parameters**:
- `block` (bool): Whether to block until a job is available

**Returns**: Request, Response, or item

#### `add_job(job, block=False)`

Adds a job to the queue.

**Parameters**:
- `job`: Job to add (Request, Response, or item)
- `block` (bool): Whether to block until the job is added

#### `size()`

Returns the size of the queue.

**Returns**: int

#### `empty()`

Checks if the queue is empty.

**Returns**: bool

#### `filter_request(job)`

Filters a request using the duplicate filter.

**Parameters**:
- `job`: Job to filter

**Returns**: bool

## Filter

Base class for duplicate filters.

```python
class Filter:
    def request_seen(self, request):
        pass
```

### Methods

#### `request_seen(request)`

Checks if a request has been seen before.

**Parameters**:
- `request` (Request): Request to check

**Returns**: bool

## Exceptions

### RetryException

Raised to force a retry of a request.

```python
class RetryException(Exception):
    pass
```

### DiscardException

Raised to discard a request.

```python
class DiscardException(Exception):
    pass
```

## Item

Base class for structured items.

```python
class Item(dict):
    pass
```

## Utility Functions

### `fingerprint(request, include_headers=None, keep_fragments=True)`

Generates a fingerprint for a request for duplicate detection.

**Parameters**:
- `request` (Request): Request to fingerprint
- `include_headers` (list, optional): Headers to include in the fingerprint
- `keep_fragments` (bool): Whether to keep URL fragments

**Returns**: bytes

### `request_from_dict(d, spider)`

Creates a Request object from a dictionary.

**Parameters**:
- `d` (dict): Dictionary representation of a request
- `spider` (Spider): Spider instance

**Returns**: Request

### `from_redis_setting(redis_url)`

Creates a Redis connection from a URL.

**Parameters**:
- `redis_url` (str): Redis URL

**Returns**: redis.StrictRedis

### `from_mysql_setting(mysql_url)`

Creates a MySQL connection from a URL.

**Parameters**:
- `mysql_url` (str): MySQL URL

**Returns**: sqlalchemy.engine.Engine
