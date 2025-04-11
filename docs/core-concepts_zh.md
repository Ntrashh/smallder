# 核心概念

本文档解释了 Smallder 框架的核心概念和组件。

## 架构概述

Smallder 遵循模块化架构，包含几个关键组件：

```
请求(Request) → 中间件(Middleware) → 下载器(Downloader) → 响应(Response) → 爬虫(Spider) → 项目(Items)
```

典型爬取过程的流程是：

1. 爬虫生成初始请求（来自 `start_urls` 或 Redis）
2. 请求通过中间件
3. 下载器获取内容
4. 创建响应并返回给爬虫
5. 爬虫处理响应并生成项目或新请求
6. 引擎管理整个过程

## 爬虫(Spider)

`Spider` 类是定义爬取逻辑的中心组件。它包含：

- 开始爬取的 URL（`start_urls`）
- 解析响应的方法（`parse`）
- 配置设置（`custom_settings`）

### 爬虫关键属性

| 属性 | 描述 | 默认值 |
|-----------|-------------|---------|
| `name` | 爬虫的唯一标识符 | "base" |
| `start_urls` | 开始爬取的 URL 列表 | [] |
| `thread_count` | 并发线程数 | CPU 核心数 × 2 |
| `max_retry` | 失败请求的最大重试次数 | 10 |
| `fastapi` | 启用/禁用监控 API | True |
| `redis_task_key` | Redis 任务队列的键 | "" |
| `pipline_mode` | 项目处理模式（"single" 或 "list"） | "single" |
| `pipline_batch` | 列表模式的批处理大小 | 100 |
| `custom_settings` | 自定义设置字典 | {} |

### 爬虫方法

| 方法 | 描述 |
|--------|-------------|
| `start_requests()` | 从 `start_urls` 生成初始请求 |
| `parse(response)` | 处理响应的默认回调 |
| `download_middleware(request)` | 在下载前处理请求 |
| `pipline(item)` | 处理生成的项目 |
| `on_start()` | 爬虫启动时调用 |
| `on_stop()` | 爬虫停止时调用 |
| `error_callback(failure)` | 发生错误时调用 |

## 请求(Request)

`Request` 类表示爬虫要发送的 HTTP 请求。

### 请求关键属性

| 属性 | 描述 | 默认值 |
|-----------|-------------|---------|
| `url` | 请求的 URL | None |
| `method` | HTTP 方法 | "GET" |
| `headers` | HTTP 头 | None |
| `params` | URL 参数 | None |
| `data` | POST 数据 | None |
| `json` | JSON 数据 | None |
| `cookies` | Cookies | None |
| `timeout` | 请求超时（秒） | 5 |
| `callback` | 处理响应的函数 | None |
| `errback` | 错误处理函数 | None |
| `meta` | 元数据字典 | {} |
| `dont_filter` | 跳过重复过滤 | False |
| `retry` | 当前重试次数 | 0 |

### 请求方法

| 方法 | 描述 |
|--------|-------------|
| `full_url()` | 返回带参数的完整 URL |
| `copy()` | 创建请求的副本 |
| `replace(**kwargs)` | 创建具有更新属性的新请求 |
| `from_curl(curl_command)` | 从 cURL 命令创建请求 |

## 响应(Response)

`Response` 类表示从网站接收到的 HTTP 响应。

### 响应关键属性

| 属性 | 描述 |
|-----------|-------------|
| `url` | 响应的 URL |
| `status_code` | HTTP 状态码 |
| `content` | 原始响应内容 |
| `request` | 原始请求对象 |
| `cookies` | 响应 cookies |
| `elapsed` | 接收响应所需时间 |

### 响应方法

| 方法 | 描述 |
|--------|-------------|
| `text` | 返回解码后的文本内容 |
| `json()` | 将响应解析为 JSON |
| `root` | 返回用于解析的 lxml HTML 元素 |
| `urljoin(url)` | 将相对 URL 与响应 URL 连接 |
| `params()` | 返回 URL 参数字典 |

## 引擎(Engine)

`Engine` 类管理爬取过程，包括：

- 线程池管理
- 请求/响应处理
- 错误处理
- 统计收集

## 中间件(Middleware)

中间件在发送前处理请求，在接收后处理响应。它们可以修改、过滤或记录请求和响应。

### 创建中间件

```python
class MyMiddleware:
    def __init__(self, spider):
        self.spider = spider
        
    def process_request(self, request):
        # 修改请求
        request.headers["X-Custom"] = "Value"
        return request
        
    def process_response(self, response):
        # 修改响应
        return response
```

### 注册中间件

```python
class MySpider(Spider):
    custom_settings = {
        "middleware_settings": {
            "path.to.MyMiddleware": 100,  # 数字越小优先级越高
        }
    }
```

## 调度器(Scheduler)

调度器管理待处理请求的队列。Smallder 支持：

- 内存调度器
- 基于 Redis 的调度器
- 自定义调度器

## 下载器(Downloader)

下载器负责发出 HTTP 请求并创建响应对象。

## 项目处理(Item Processing)

爬虫生成的项目由 `pipline` 方法处理，可以自定义该方法以多种方式存储数据，例如：

- 写入文件
- 存储在数据库中
- 发送到 API

## 错误处理

Smallder 提供了几种处理错误的机制：

- 特定请求的 `errback` 函数
- 通用错误处理的 `error_callback` 方法
- 失败请求的自动重试
- 异常类：`RetryException` 和 `DiscardException`

---

[切换到英文文档](core-concepts.md)
