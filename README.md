# Smallder - A Lightweight Web Crawling Framework
[![PyPI Downloads](https://static.pepy.tech/badge/smallder)](https://pepy.tech/projects/smallder)  [![PyPI Downloads](https://static.pepy.tech/badge/smallder/month)](https://pepy.tech/projects/smallder) [![PyPI Downloads](https://static.pepy.tech/badge/smallder/week)](https://pepy.tech/projects/smallder)

## Introduction

Smaller is a lightweight, easy-to-use web crawling framework designed for simplicity and efficiency. It provides a powerful yet straightforward approach to building web crawlers with features like:

- Multi-threaded architecture
- Built-in middleware system
- Redis integration for distributed crawling
- MySQL integration for data storage
- Customizable request and response handling
- Real-time statistics and monitoring

GitHub: https://github.com/Ntrashh/smallder

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Introduction and Overview](docs/README.md) / [中文](docs/README_zh.md)
- [Core Concepts](docs/core-concepts.md) / [中文](docs/core-concepts_zh.md)
- [Advanced Usage](docs/advanced-usage.md) / [中文](docs/advanced-usage_zh.md)
- [API Reference](docs/api-reference.md) / [中文](docs/api-reference_zh.md)
- [Examples](docs/examples.md) / [中文](docs/examples_zh.md)
- [How to Use Documentation](docs/how-to-use-docs.md) / [中文](docs/how-to-use-docs_zh.md)



## Requirements
- Python 3.7.0+
- Works on Linux, Windows, macOS

## Installation
```bash
pip install smallder
```

## Quick Start

Create a new spider:
```bash
smallder create -s demo_spider
```

```python
from typing import Any
from smallder import Spider, Request, Response

class Demo(Spider):
    name = "demo"
    fastapi = True  # 控制内部统计api的数据
    redis_task_key = ""  # 任务池key如果存在值,则直接从redis中去任务,需要重写make_request_for_redis
    start_urls = []
    max_retry: int = 10  # 重试次数
    # thread_count = 0       # 线程总数 默认为cpu核心数两倍线程
    # batch_size = 0         # 批次从redis中获取多少数据 不使用redis不需要次参数
    # pipline_mode = "list"  # 两种模式 single代表单条入库,list代表多条入库 默认为single
    # pipline_batch = 100    # 只有在pipline_mode=list时生效,代表多少条item进入pipline,默认100
    # save_failed_request = False  # 保存错误请求到redis,不使用redis可不用开启
    custom_settings = {
        # "middleware_settings": {}, # 设置中间件
        # "mysql": "",  # "mysql://xxx:xxxxx@host:port/db_name"
        # "redis": "" # "redis://xxx:xxxxx@host:port/db_name"
    }

    # def __init__(self, param):
    #     self.param = param

    def parse(self, response: Response) -> Any:
        self.log.info(response)

    def download_middleware(self, request: Request) -> Request:
        request.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/108.0.0.0 Safari/537.36"
        }
        return request


if __name__ == "__main__":
    Demo.start()
    # Demo.start(param="param传递")

```





## Features

- **Simple API**: Easy to learn and use
- **Asynchronous + Multi-threaded**: Efficient crawling with thread pool
- **Middleware System**: Customize request/response processing
- **Redis Integration**: Distributed crawling support
- **MySQL Integration**: Built-in database storage
- **Error Handling**: Automatic retry and error callbacks
- **Monitoring**: Real-time statistics with FastAPI

## Contact

If you have any questions or suggestions about Smallder, please contact me:

WeChat:

![wechat](https://user-images.githubusercontent.com/109586486/210029580-4bb2f7bb-ed19-4971-ad0a-788aa659e2ff.jpg)

Email: yinghui0214@163.com


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Ntrashh/smallder&type=Date)](https://star-history.com/#Ntrashh/smallder&Date)


##
<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.png" alt="PyCharm logo."  width="30%" >