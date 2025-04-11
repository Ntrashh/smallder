# Smallder 文档

欢迎阅读 Smallder 的官方文档，Smallder 是一个轻量级的网络爬虫框架。

## 目录

- [简介](#简介)
- [安装](#安装)
- [快速开始](#快速开始)
- [核心概念](core-concepts_zh.md)
- [高级用法](advanced-usage_zh.md)
- [API 参考](api-reference_zh.md)
- [示例](examples_zh.md)
- [如何使用本文档](how-to-use-docs_zh.md)
- [贡献](#贡献)

## 简介

Smallder 是一个轻量级、易于使用的网络爬虫框架，专为简单高效而设计。它提供了强大而直观的方法来构建网络爬虫，具有以下特点：

- 多线程架构
- 内置中间件系统
- Redis 集成，支持分布式爬取
- MySQL 集成，方便数据存储
- 可自定义的请求和响应处理
- 实时统计和监控

无论您是构建简单的数据抓取工具还是复杂的分布式爬虫，Smallder 都能以最少的配置提供所需的工具。

## 安装

### 要求

- Python 3.7+
- 支持 Linux、Windows、macOS

### 从 PyPI 安装

```bash
pip install smallder
```

## 快速开始

### 创建爬虫

使用命令行工具创建新爬虫：

```bash
smallder create -s my_spider
```

这将创建一个包含基本爬虫模板的新文件 `my_spider.py`。

### 基本爬虫示例

```python
from typing import Any
from smallder import Spider, Request, Response

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    
    def parse(self, response: Response) -> Any:
        # 从响应中提取数据
        self.log.info(f"已爬取: {response.url}")
        
        # 可以生成项目（字典）进行处理
        yield {"url": response.url, "title": response.root.xpath("//title/text()")[0]}
        
        # 或者生成新的请求以跟踪链接
        for link in response.root.xpath("//a/@href"):
            yield Request(url=response.urljoin(link), callback=self.parse_detail)
    
    def parse_detail(self, response: Response) -> Any:
        # 处理详情页面
        yield {"url": response.url, "detail": True}
    
    def download_middleware(self, request: Request) -> Request:
        # 在发送前自定义请求
        request.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        return request

if __name__ == "__main__":
    MySpider.start()
```

### 运行爬虫

只需运行 Python 文件：

```bash
python my_spider.py
```

## 核心概念

有关 Smallder 核心概念的更详细信息，请参阅[核心概念](core-concepts_zh.md)文档。

## 高级用法

有关高级用法场景，请参阅[高级用法](advanced-usage_zh.md)文档。

## API 参考

有关详细的 API 文档，请参阅 [API 参考](api-reference_zh.md)。

## 示例

有关爬虫示例和用例，请参阅[示例](examples_zh.md)文档。

## 贡献

欢迎贡献！请随时提交 Pull Request。

---

[切换到英文文档](README.md)
