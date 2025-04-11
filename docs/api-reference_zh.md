# API 参考

本文档提供了 Smallder 框架中可用的类和方法的详细信息。

## Spider

所有爬虫的基类。

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

### 类属性

| 属性 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | str | 爬虫的唯一标识符 |
| `fastapi` | bool | 启用/禁用监控 API |
| `server` | redis.StrictRedis | Redis 连接（自动设置） |
| `mysql_server` | sqlalchemy.engine.Engine | MySQL 连接（自动设置） |
| `batch_size` | int | 一次从 Redis 获取的任务数量 |
| `redis_task_key` | str | Redis 任务队列的键 |
| `start_urls` | list | 开始爬取的 URL 列表 |
| `thread_count` | int | 并发线程数 |
| `max_retry` | int | 失败请求的最大重试次数 |
| `save_failed_request` | bool | 将失败的请求保存到 Redis |
| `pipline_mode` | str | 项目处理模式（"single" 或 "list"） |
| `pipline_batch` | int | 列表模式的批处理大小 |
| `custom_settings` | dict | 自定义设置字典 |

### 方法

#### `start_requests()`

从 `start_urls` 生成初始请求。

**返回值**: `Request` 对象的生成器

#### `parse(response)`

处理响应的默认回调。

**参数**:
- `response` (Response): 要解析的响应

**返回值**: 项目或 `Request` 对象的生成器

#### `download_middleware(request)`

在下载前处理请求。

**参数**:
- `request` (Request): 要处理的请求

**返回值**: 修改后的 `Request` 对象

#### `make_request_for_redis(data)`

将 Redis 数据转换为 `Request` 对象。

**参数**:
- `data` (bytes): 来自 Redis 的数据

**返回值**: `Request` 对象或 `Request` 对象列表

#### `pipline(item)`

处理生成的项目。

**参数**:
- `item` (dict): 要处理的项目（或在 "list" 模式下的项目列表）

#### `on_start()`

爬虫启动时调用。

#### `on_stop()`

爬虫停止时调用。

#### `error_callback(failure)`

发生错误时调用。

**参数**:
- `failure` (Failure): 包含错误信息的对象

**返回值**: 异常对象

#### `inc_value(key_name)`

增加统计计数器。

**参数**:
- `key_name` (str): 要增加的计数器名称

#### `connect_start_signal(func)`

将函数连接到爬虫启动信号。

**参数**:
- `func` (callable): 爬虫启动时调用的函数

#### `connect_stop_signal(func)`

将函数连接到爬虫停止信号。

**参数**:
- `func` (callable): 爬虫停止时调用的函数

#### `setup_server()`

设置 Redis 和 MySQL 连接。

#### `setup_redis()`

设置 Redis 连接。

#### `setup_mysql()`

设置 MySQL 连接。

#### `start(**kwargs)`

启动爬虫的类方法。

**参数**:
- `**kwargs`: 传递给爬虫构造函数的关键字参数

#### `debug(**kwargs)`

在调试模式下运行爬虫的类方法。

**参数**:
- `**kwargs`: 传递给爬虫构造函数的关键字参数

**返回值**: 爬虫实例

## Request

表示 HTTP 请求。

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

### 参数

| 参数 | 类型 | 描述 | 默认值 |
|-----------|------|-------------|---------|
| `method` | str | HTTP 方法 | "get" |
| `url` | str | 请求的 URL | None |
| `headers` | dict | HTTP 头 | None |
| `params` | dict | URL 参数 | None |
| `data` | dict/str | POST 数据 | None |
| `json` | dict | JSON 数据 | None |
| `cookies` | dict | Cookies | None |
| `timeout` | int | 请求超时（秒） | 5 |
| `callback` | callable | 处理响应的函数 | None |
| `errback` | callable | 错误处理函数 | None |
| `meta` | dict | 元数据字典 | None |
| `referer` | str | 引用 URL | None |
| `proxies` | dict | 代理设置 | None |
| `dont_filter` | bool | 跳过重复过滤 | False |
| `verify` | bool | 验证 SSL 证书 | False |
| `allow_redirects` | bool | 跟随重定向 | True |
| `priority` | int | 请求优先级 | 0 |
| `fetch` | callable | 自定义获取函数 | None |
| `retry` | int | 当前重试次数 | 0 |

### 属性

#### `meta`

用于存储元数据的字典。

**返回值**: dict

#### `referer`

引用 URL。

**返回值**: str

#### `headers`

添加了 "Connection: close" 的 HTTP 头。

**返回值**: dict

### 方法

#### `full_url()`

返回带参数的完整 URL。

**返回值**: str

#### `copy()`

创建请求的副本。

**返回值**: Request

#### `replace(**kwargs)`

创建具有更新属性的新请求。

**参数**:
- `**kwargs`: 要更新的属性

**返回值**: Request

#### `to_dict(spider)`

将请求转换为字典以进行序列化。

**参数**:
- `spider` (Spider): 爬虫实例

**返回值**: dict

#### `from_curl(curl_command, **kwargs)`

从 cURL 命令创建请求的类方法。

**参数**:
- `curl_command` (str): cURL 命令
- `**kwargs`: 附加参数

**返回值**: Request

## Response

表示 HTTP 响应。

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

### 参数

| 参数 | 类型 | 描述 | 默认值 |
|-----------|------|-------------|---------|
| `url` | str | 响应的 URL | None |
| `status_code` | int | HTTP 状态码 | 200 |
| `content` | bytes | 原始响应内容 | None |
| `request` | Request | 原始请求对象 | None（必需） |
| `encoding` | str | 内容编码 | "utf-8" |
| `cookies` | dict | 响应 cookies | None |
| `elapsed` | float | 接收响应所需时间 | 0 |

### 属性

#### `meta`

原始请求的元数据。

**返回值**: dict

#### `referer`

原始请求的引用。

**返回值**: str

#### `text`

解码后的内容文本。

**返回值**: str

#### `ok`

状态码是否为 200。

**返回值**: bool

#### `root`

用于解析的 lxml HTML 元素。

**返回值**: lxml.html.HtmlElement

### 方法

#### `json(**kwargs)`

将响应解析为 JSON。

**参数**:
- `**kwargs`: 传递给 `json.loads()` 的参数

**返回值**: dict/list

#### `urljoin(url)`

将相对 URL 与响应 URL 连接。

**参数**:
- `url` (str): 相对 URL

**返回值**: str

#### `params()`

返回 URL 参数字典。

**返回值**: dict

#### `replace(**kwargs)`

创建具有更新属性的新响应。

**参数**:
- `**kwargs`: 要更新的属性

**返回值**: Response

## Engine

管理爬取过程。

```python
class Engine:
    def __init__(self, spider, **kwargs):
        # ...
```

### 参数

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `spider` | Spider class | 要实例化的爬虫类 |
| `**kwargs` | dict | 传递给爬虫构造函数的参数 |

### 方法

#### `engine()`

在正常模式下运行引擎。

#### `debug()`

在调试模式下运行引擎。

**返回值**: 爬虫实例

#### `process_request(request)`

处理请求。

**参数**:
- `request` (Request): 要处理的请求

#### `process_response(response)`

处理响应。

**参数**:
- `response` (Response): 要处理的响应

#### `process_item(item)`

处理项目。

**参数**:
- `item` (dict): 要处理的项目

#### `handler_request_retry(request)`

处理请求重试。

**参数**:
- `request` (Request): 要重试的请求

#### `process_callback_error(e, request, response=None)`

处理回调错误。

**参数**:
- `e` (Exception): 发生的异常
- `request` (Request): 导致错误的请求
- `response` (Response, optional): 导致错误的响应

## Downloader

处理 HTTP 请求。

```python
class Downloader:
    def __init__(self, spider):
        self.spider = spider
```

### 参数

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `spider` | Spider | 爬虫实例 |

### 方法

#### `fetch(request)`

获取请求响应的类方法。

**参数**:
- `request` (Request): 要获取的请求

**返回值**: Response

#### `download(request)`

下载请求的响应，如果提供了自定义获取方法则使用它。

**参数**:
- `request` (Request): 要下载的请求

**返回值**: Response

## MiddlewareManager

管理中间件组件。

```python
class MiddlewareManager:
    def __init__(self, spider):
        self.spider = spider
        self.middlewares = spider.custom_settings.get("middleware_settings", {})
        self.loaded_middlewares = []
```

### 参数

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `spider` | Spider | 爬虫实例 |

### 方法

#### `load_middlewares()`

加载中间件组件。

#### `process_request(request)`

通过所有中间件组件处理请求。

**参数**:
- `request` (Request): 要处理的请求

**返回值**: 修改后的 Request

#### `process_response(response)`

通过所有中间件组件处理响应。

**参数**:
- `response` (Response): 要处理的响应

**返回值**: 修改后的 Response

## Scheduler

调度器的基类。

```python
class Scheduler:
    def __init__(self, spider, dup_filter):
        self.spider = spider
        self.batch_size = self.spider.batch_size or self.spider.thread_count * 10
        self.dup_filter = dup_filter
```

### 参数

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `spider` | Spider | 爬虫实例 |
| `dup_filter` | Filter | 重复过滤器实例 |

### 方法

#### `next_job(block=False)`

从队列中获取下一个任务。

**参数**:
- `block` (bool): 是否阻塞直到有任务可用

**返回值**: Request, Response 或项目

#### `add_job(job, block=False)`

将任务添加到队列。

**参数**:
- `job`: 要添加的任务（Request, Response 或项目）
- `block` (bool): 是否阻塞直到任务被添加

#### `size()`

返回队列的大小。

**返回值**: int

#### `empty()`

检查队列是否为空。

**返回值**: bool

#### `filter_request(job)`

使用重复过滤器过滤请求。

**参数**:
- `job`: 要过滤的任务

**返回值**: bool

## Filter

重复过滤器的基类。

```python
class Filter:
    def request_seen(self, request):
        pass
```

### 方法

#### `request_seen(request)`

检查请求是否已经被看到。

**参数**:
- `request` (Request): 要检查的请求

**返回值**: bool

## 异常

### RetryException

用于强制重试请求的异常。

```python
class RetryException(Exception):
    pass
```

### DiscardException

用于丢弃请求的异常。

```python
class DiscardException(Exception):
    pass
```

## Item

结构化项目的基类。

```python
class Item(dict):
    pass
```

## 实用函数

### `fingerprint(request, include_headers=None, keep_fragments=True)`

为重复检测生成请求的指纹。

**参数**:
- `request` (Request): 要生成指纹的请求
- `include_headers` (list, optional): 要包含在指纹中的头
- `keep_fragments` (bool): 是否保留 URL 片段

**返回值**: bytes

### `request_from_dict(d, spider)`

从字典创建 Request 对象。

**参数**:
- `d` (dict): 请求的字典表示
- `spider` (Spider): 爬虫实例

**返回值**: Request

### `from_redis_setting(redis_url)`

从 URL 创建 Redis 连接。

**参数**:
- `redis_url` (str): Redis URL

**返回值**: redis.StrictRedis

### `from_mysql_setting(mysql_url)`

从 URL 创建 MySQL 连接。

**参数**:
- `mysql_url` (str): MySQL URL

**返回值**: sqlalchemy.engine.Engine

---

[切换到英文文档](api-reference.md)
