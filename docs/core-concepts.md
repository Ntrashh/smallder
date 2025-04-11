# Core Concepts

This document explains the core concepts and components of the Smallder framework.

[切换到中文文档](core-concepts_zh.md)

## Architecture Overview

Smallder follows a modular architecture with several key components:

```
Request → Middleware → Downloader → Response → Spider → Items
```

The flow of a typical crawl process is:

1. Spider generates initial requests (from `start_urls` or Redis)
2. Requests pass through middleware
3. Downloader fetches the content
4. Response is created and passed back to the Spider
5. Spider processes the response and yields items or new requests
6. Engine manages the entire process

## Spider

The `Spider` class is the central component where you define the crawling logic. It contains:

- URLs to start crawling (`start_urls`)
- Methods to parse responses (`parse`)
- Configuration settings (`custom_settings`)

### Key Spider Attributes

| Attribute | Description | Default |
|-----------|-------------|---------|
| `name` | Unique identifier for the spider | "base" |
| `start_urls` | List of URLs to start crawling | [] |
| `thread_count` | Number of concurrent threads | CPU count × 2 |
| `max_retry` | Maximum retry attempts for failed requests | 10 |
| `fastapi` | Enable/disable monitoring API | True |
| `redis_task_key` | Redis key for task queue | "" |
| `pipline_mode` | Item processing mode ("single" or "list") | "single" |
| `pipline_batch` | Batch size for list mode | 100 |
| `custom_settings` | Dictionary of custom settings | {} |

### Spider Methods

| Method | Description |
|--------|-------------|
| `start_requests()` | Generates initial requests from `start_urls` |
| `parse(response)` | Default callback for processing responses |
| `download_middleware(request)` | Processes requests before downloading |
| `pipline(item)` | Processes yielded items |
| `on_start()` | Called when the spider starts |
| `on_stop()` | Called when the spider stops |
| `error_callback(failure)` | Called when an error occurs |

## Request

The `Request` class represents an HTTP request to be sent by the crawler.

### Key Request Attributes

| Attribute | Description | Default |
|-----------|-------------|---------|
| `url` | URL to request | None |
| `method` | HTTP method | "GET" |
| `headers` | HTTP headers | None |
| `params` | URL parameters | None |
| `data` | POST data | None |
| `json` | JSON data | None |
| `cookies` | Cookies | None |
| `timeout` | Request timeout in seconds | 5 |
| `callback` | Function to call with the response | None |
| `errback` | Function to call on error | None |
| `meta` | Metadata dictionary | {} |
| `dont_filter` | Skip duplicate filtering | False |
| `retry` | Current retry count | 0 |

### Request Methods

| Method | Description |
|--------|-------------|
| `full_url()` | Returns the complete URL with parameters |
| `copy()` | Creates a copy of the request |
| `replace(**kwargs)` | Creates a new request with updated attributes |
| `from_curl(curl_command)` | Creates a request from a cURL command |

## Response

The `Response` class represents an HTTP response received from a website.

### Key Response Attributes

| Attribute | Description |
|-----------|-------------|
| `url` | URL of the response |
| `status_code` | HTTP status code |
| `content` | Raw response content |
| `request` | Original request object |
| `cookies` | Response cookies |
| `elapsed` | Time taken to receive the response |

### Response Methods

| Method | Description |
|--------|-------------|
| `text` | Returns the decoded content as text |
| `json()` | Parses the response as JSON |
| `root` | Returns an lxml HTML element for parsing |
| `urljoin(url)` | Joins a relative URL with the response URL |
| `params()` | Returns the URL parameters as a dictionary |

## Engine

The `Engine` class manages the crawling process, including:

- Thread pool management
- Request/response processing
- Error handling
- Statistics collection

## Middleware

Middlewares process requests before they are sent and responses after they are received. They can modify, filter, or log requests and responses.

### Creating a Middleware

```python
class MyMiddleware:
    def __init__(self, spider):
        self.spider = spider

    def process_request(self, request):
        # Modify request
        request.headers["X-Custom"] = "Value"
        return request

    def process_response(self, response):
        # Modify response
        return response
```

### Registering a Middleware

```python
class MySpider(Spider):
    custom_settings = {
        "middleware_settings": {
            "path.to.MyMiddleware": 100,  # Lower numbers have higher priority
        }
    }
```

## Scheduler

The scheduler manages the queue of requests to be processed. Smallder supports:

- In-memory scheduler
- Redis-based scheduler
- Custom schedulers

## Downloader

The downloader is responsible for making HTTP requests and creating response objects.

## Item Processing

Items yielded by the spider are processed by the `pipline` method, which can be customized to store data in various ways, such as:

- Writing to files
- Storing in a database
- Sending to an API

## Error Handling

Smallder provides several mechanisms for handling errors:

- `errback` functions for specific requests
- `error_callback` method for general error handling
- Automatic retry for failed requests
- Exception classes: `RetryException` and `DiscardException`
