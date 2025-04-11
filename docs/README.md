# Smallder Documentation

Welcome to the official documentation for Smallder, a lightweight, asynchronous web crawling framework.

[切换到中文文档](README_zh.md)

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [How to Use This Documentation](how-to-use-docs.md)
- [Contributing](#contributing)

## Introduction

Smallder is a lightweight, easy-to-use web crawling framework designed for simplicity and efficiency. It provides a powerful yet straightforward approach to building web crawlers with features like:

- Asynchronous + multi-threaded architecture
- Built-in middleware system
- Redis integration for distributed crawling
- MySQL integration for data storage
- Customizable request and response handling
- Real-time statistics and monitoring

Whether you're building a simple scraper or a complex distributed crawler, Smallder provides the tools you need with minimal configuration.

## Installation

### Requirements

- Python 3.7+
- Works on Linux, Windows, macOS

### Install from PyPI

```bash
pip install smallder
```

## Quick Start

### Creating a Spider

Use the command-line tool to create a new spider:

```bash
smallder create -s my_spider
```

This will create a new file `my_spider.py` with a basic spider template.

### Basic Spider Example

```python
from typing import Any
from smallder import Spider, Request, Response

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def parse(self, response: Response) -> Any:
        # Extract data from the response
        self.log.info(f"Crawled: {response.url}")

        # You can yield items (dictionaries) for processing
        yield {"url": response.url, "title": response.root.xpath("//title/text()")[0]}

        # Or yield new requests to follow
        for link in response.root.xpath("//a/@href"):
            yield Request(url=response.urljoin(link), callback=self.parse_detail)

    def parse_detail(self, response: Response) -> Any:
        # Process detail pages
        yield {"url": response.url, "detail": True}

    def download_middleware(self, request: Request) -> Request:
        # Customize request before sending
        request.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        return request

if __name__ == "__main__":
    MySpider.start()
```

### Running the Spider

Simply run the Python file:

```bash
python my_spider.py
```

## Core Concepts

For more detailed information about Smallder's core concepts, see the [Core Concepts](core-concepts.md) documentation.

## Advanced Usage

For advanced usage scenarios, see the [Advanced Usage](advanced-usage.md) documentation.

## API Reference

For detailed API documentation, see the [API Reference](api-reference.md).

## Examples

For example spiders and use cases, see the [Examples](examples.md) documentation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
