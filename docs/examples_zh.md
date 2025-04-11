# 示例

本文档提供了使用 Smallder 框架进行各种网络爬取任务的实用示例。

## 基本爬虫

一个简单的爬虫，爬取网站并提取基本信息。

```python
from typing import Any
from smallder import Spider, Request, Response

class BasicSpider(Spider):
    name = "basic_spider"
    start_urls = ["https://quotes.toscrape.com/"]
    
    def parse(self, response: Response) -> Any:
        # 提取引用
        for quote in response.root.xpath("//div[@class='quote']"):
            text = quote.xpath("./span[@class='text']/text()")[0]
            author = quote.xpath("./span/small[@class='author']/text()")[0]
            
            yield {
                "text": text,
                "author": author
            }
        
        # 跟踪分页
        next_page = response.root.xpath("//li[@class='next']/a/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )

if __name__ == "__main__":
    BasicSpider.start()
```

## 电子商务爬虫

一个爬取电子商务网站并提取产品信息的爬虫。

```python
from typing import Any
from smallder import Spider, Request, Response

class EcommerceSpider(Spider):
    name = "ecommerce_spider"
    start_urls = ["https://example-ecommerce.com/products"]
    
    def parse(self, response: Response) -> Any:
        # 提取产品链接
        for product_link in response.root.xpath("//div[@class='product']/a/@href"):
            yield Request(
                url=response.urljoin(product_link),
                callback=self.parse_product
            )
        
        # 跟踪分页
        next_page = response.root.xpath("//a[@class='next-page']/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )
    
    def parse_product(self, response: Response) -> Any:
        # 提取产品详情
        product = {
            "url": response.url,
            "name": response.root.xpath("//h1[@class='product-name']/text()")[0].strip(),
            "price": response.root.xpath("//span[@class='price']/text()")[0].strip(),
            "description": "".join(response.root.xpath("//div[@class='description']//text()")).strip()
        }
        
        # 提取图片
        images = response.root.xpath("//div[@class='product-images']//img/@src")
        product["images"] = [response.urljoin(img) for img in images]
        
        yield product

if __name__ == "__main__":
    EcommerceSpider.start()
```

## API 爬虫

一个与 JSON API 交互的爬虫。

```python
from typing import Any
import json
from smallder import Spider, Request, Response

class ApiSpider(Spider):
    name = "api_spider"
    start_urls = ["https://api.example.com/items?page=1"]
    
    def download_middleware(self, request: Request) -> Request:
        request.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Authorization": "Bearer YOUR_API_TOKEN"
        }
        return request
    
    def parse(self, response: Response) -> Any:
        data = response.json()
        
        # 提取项目
        for item in data["items"]:
            yield {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"]
            }
        
        # 跟踪分页
        if data["has_next_page"]:
            next_page = data["next_page_url"]
            yield Request(
                url=next_page,
                callback=self.parse
            )

if __name__ == "__main__":
    ApiSpider.start()
```

## 登录和会话处理

一个登录网站并维护会话的爬虫。

```python
from typing import Any
from smallder import Spider, Request, Response

class LoginSpider(Spider):
    name = "login_spider"
    start_urls = ["https://example.com/login"]
    
    def parse(self, response: Response) -> Any:
        # 提取 CSRF 令牌
        csrf_token = response.root.xpath("//input[@name='csrf_token']/@value")[0]
        
        # 提交登录表单
        yield Request(
            url="https://example.com/login",
            method="POST",
            data={
                "username": "your_username",
                "password": "your_password",
                "csrf_token": csrf_token
            },
            callback=self.after_login,
            dont_filter=True  # 不过滤掉这个 URL，即使我们之前见过它
        )
    
    def after_login(self, response: Response) -> Any:
        # 检查登录是否成功
        if "Welcome" in response.text:
            self.log.info("登录成功！")
            
            # 访问受保护页面
            yield Request(
                url="https://example.com/protected-area",
                callback=self.parse_protected
            )
        else:
            self.log.error("登录失败！")
    
    def parse_protected(self, response: Response) -> Any:
        # 从受保护页面提取数据
        yield {
            "url": response.url,
            "title": response.root.xpath("//title/text()")[0]
        }

if __name__ == "__main__":
    LoginSpider.start()
```

## 使用 Redis 的分布式爬虫

一个使用 Redis 进行分布式爬取的爬虫。

```python
from typing import Any
from smallder import Spider, Request, Response

class DistributedSpider(Spider):
    name = "distributed_spider"
    redis_task_key = "distributed_spider:tasks"
    
    custom_settings = {
        "redis": "redis://localhost:6379/0"
    }
    
    def make_request_for_redis(self, data):
        # 将 Redis 数据转换为 Request 对象
        url = data.decode('utf-8')
        return Request(url=url, callback=self.parse)
    
    def parse(self, response: Response) -> Any:
        # 提取数据
        title = response.root.xpath("//title/text()")[0]
        
        yield {
            "url": response.url,
            "title": title
        }
        
        # 提取链接
        for link in response.root.xpath("//a/@href"):
            full_url = response.urljoin(link)
            yield Request(url=full_url, callback=self.parse)

if __name__ == "__main__":
    DistributedSpider.start()
```

要将 URL 添加到 Redis 队列：

```python
import redis
r = redis.StrictRedis.from_url("redis://localhost:6379/0")
r.lpush("distributed_spider:tasks", "https://example.com")
```

## 数据库集成

一个将数据存储在 MySQL 数据库中的爬虫。

```python
from typing import Any
from smallder import Spider, Request, Response

class DatabaseSpider(Spider):
    name = "database_spider"
    start_urls = ["https://quotes.toscrape.com/"]
    
    custom_settings = {
        "mysql": "mysql://username:password@localhost:3306/scraping"
    }
    
    def parse(self, response: Response) -> Any:
        # 提取引用
        for quote in response.root.xpath("//div[@class='quote']"):
            text = quote.xpath("./span[@class='text']/text()")[0]
            author = quote.xpath("./span/small[@class='author']/text()")[0]
            
            yield {
                "text": text,
                "author": author
            }
        
        # 跟踪分页
        next_page = response.root.xpath("//li[@class='next']/a/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )
    
    def pipline(self, item):
        # 将项目存储在 MySQL 中
        if self.mysql_server:
            with self.mysql_server.connect() as connection:
                connection.execute(
                    "INSERT INTO quotes (text, author) VALUES (:text, :author)",
                    item
                )

if __name__ == "__main__":
    DatabaseSpider.start()
```

## 自定义中间件

一个带有用于处理 cookies 和头的自定义中间件的爬虫。

```python
# middleware/custom.py
class CookieMiddleware:
    def __init__(self, spider):
        self.spider = spider
    
    def process_request(self, request):
        # 为所有请求添加 cookies
        request.cookies = request.cookies or {}
        request.cookies.update({
            "session_id": "12345",
            "user_preference": "dark_mode"
        })
        return request

class UserAgentMiddleware:
    def __init__(self, spider):
        self.spider = spider
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ]
        self.current_index = 0
    
    def process_request(self, request):
        # 轮换用户代理
        request.headers = request.headers or {}
        request.headers["User-Agent"] = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return request

# spider.py
from typing import Any
from smallder import Spider, Request, Response

class MiddlewareSpider(Spider):
    name = "middleware_spider"
    start_urls = ["https://httpbin.org/cookies", "https://httpbin.org/user-agent"]
    
    custom_settings = {
        "middleware_settings": {
            "middleware.custom.CookieMiddleware": 100,
            "middleware.custom.UserAgentMiddleware": 200
        }
    }
    
    def parse(self, response: Response) -> Any:
        yield {
            "url": response.url,
            "data": response.json()
        }

if __name__ == "__main__":
    MiddlewareSpider.start()
```

## 错误处理

一个带有自定义错误处理的爬虫。

```python
from typing import Any
from requests.exceptions import RequestException
from smallder import Spider, Request, Response
from smallder.core.error import RetryException, DiscardException

class ErrorHandlingSpider(Spider):
    name = "error_handling_spider"
    start_urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
        "https://httpbin.org/status/500",
        "https://non-existent-domain.example"
    ]
    
    def parse(self, response: Response) -> Any:
        if response.status_code == 404:
            # 不重试 404 错误
            raise DiscardException(f"页面未找到: {response.url}")
        
        if response.status_code == 500:
            # 强制重试 500 错误
            raise RetryException(f"服务器错误: {response.url}")
        
        # 处理成功的响应
        yield {
            "url": response.url,
            "status": response.status_code
        }
    
    def error_callback(self, failure):
        # 记录错误
        self.log.error(f"处理 {failure.request.url} 时出错: {failure.exception}")
        
        if isinstance(failure.exception, RequestException):
            # 连接错误、DNS 失败等
            self.log.error(f"请求异常: {failure.exception}")
        
        # 返回异常以允许正常的错误处理
        return failure.exception

if __name__ == "__main__":
    ErrorHandlingSpider.start()
```

## 自定义请求获取

一个具有特定请求自定义获取方法的爬虫。

```python
from typing import Any
import json
from smallder import Spider, Request, Response

class CustomFetchSpider(Spider):
    name = "custom_fetch_spider"
    start_urls = ["https://example.com"]
    
    def custom_fetch(self, request):
        # 模拟响应，无需实际发出 HTTP 请求
        if "api" in request.url:
            content = json.dumps({
                "items": [
                    {"id": 1, "name": "项目 1"},
                    {"id": 2, "name": "项目 2"}
                ]
            }).encode('utf-8')
            
            return Response(
                url=request.url,
                status_code=200,
                content=content,
                request=request
            )
        
        # 对于其他 URL，使用默认获取方法
        return None
    
    def parse(self, response: Response) -> Any:
        # 提取链接
        for link in response.root.xpath("//a/@href"):
            full_url = response.urljoin(link)
            
            # 对 API URL 使用自定义获取
            if "api" in full_url:
                yield Request(
                    url=full_url,
                    callback=self.parse_api,
                    fetch=self.custom_fetch
                )
            else:
                yield Request(
                    url=full_url,
                    callback=self.parse
                )
    
    def parse_api(self, response: Response) -> Any:
        # 处理 API 响应
        data = response.json()
        
        for item in data["items"]:
            yield {
                "id": item["id"],
                "name": item["name"]
            }

if __name__ == "__main__":
    CustomFetchSpider.start()
```

## 批处理

一个批量处理项目的爬虫。

```python
from typing import Any
from smallder import Spider, Request, Response

class BatchSpider(Spider):
    name = "batch_spider"
    start_urls = ["https://quotes.toscrape.com/"]
    
    # 启用批处理
    pipline_mode = "list"
    pipline_batch = 10  # 每批处理 10 个项目
    
    def parse(self, response: Response) -> Any:
        # 提取引用
        for quote in response.root.xpath("//div[@class='quote']"):
            text = quote.xpath("./span[@class='text']/text()")[0]
            author = quote.xpath("./span/small[@class='author']/text()")[0]
            
            yield {
                "text": text,
                "author": author
            }
        
        # 跟踪分页
        next_page = response.root.xpath("//li[@class='next']/a/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )
    
    def pipline(self, items):
        # 处理一批项目
        if not items:
            return
            
        self.log.info(f"处理 {len(items)} 个项目的批次")
        
        # 示例：写入文件
        with open("quotes.jsonl", "a") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    BatchSpider.start()
```

## 向爬虫传递参数

一个在启动时接受参数的爬虫。

```python
from typing import Any
from smallder import Spider, Request, Response

class ParameterizedSpider(Spider):
    name = "parameterized_spider"
    
    def __init__(self, category=None, pages=1):
        self.category = category or "books"
        self.pages = int(pages)
    
    def start_requests(self):
        for page in range(1, self.pages + 1):
            url = f"https://example.com/{self.category}?page={page}"
            yield Request(url=url, callback=self.parse)
    
    def parse(self, response: Response) -> Any:
        # 提取项目
        for item in response.root.xpath("//div[@class='item']"):
            name = item.xpath("./h2/text()")[0]
            price = item.xpath("./span[@class='price']/text()")[0]
            
            yield {
                "category": self.category,
                "name": name,
                "price": price
            }

if __name__ == "__main__":
    # 向爬虫传递参数
    ParameterizedSpider.start(category="electronics", pages=3)
```

## 使用 cURL 命令

一个从 cURL 命令创建请求的爬虫。

```python
from typing import Any
from smallder import Spider, Request, Response

class CurlSpider(Spider):
    name = "curl_spider"
    
    def start_requests(self):
        # 从 cURL 命令创建请求
        curl_cmd = """
        curl 'https://api.example.com/items' \
          -H 'User-Agent: Mozilla/5.0' \
          -H 'Accept: application/json' \
          -H 'Content-Type: application/json' \
          -H 'Authorization: Bearer TOKEN' \
          --data-raw '{"query":"test","page":1}'
        """
        
        yield Request.from_curl(curl_cmd, callback=self.parse_api)
    
    def parse_api(self, response: Response) -> Any:
        data = response.json()
        
        for item in data.get("items", []):
            yield {
                "id": item["id"],
                "name": item["name"]
            }
            
        # 如果有下一页，从 cURL 创建另一个请求
        if data.get("has_next_page"):
            next_page = data.get("page", 1) + 1
            
            curl_cmd = f"""
            curl 'https://api.example.com/items' \
              -H 'User-Agent: Mozilla/5.0' \
              -H 'Accept: application/json' \
              -H 'Content-Type: application/json' \
              -H 'Authorization: Bearer TOKEN' \
              --data-raw '{{"query":"test","page":{next_page}}}'
            """
            
            yield Request.from_curl(curl_cmd, callback=self.parse_api)

if __name__ == "__main__":
    CurlSpider.start()
```

---

[切换到英文文档](examples.md)
