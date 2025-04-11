# Examples

This document provides practical examples of using the Smallder framework for various web scraping tasks.

[切换到中文文档](examples_zh.md)

## Basic Spider

A simple spider that crawls a website and extracts basic information.

```python
from typing import Any
from smallder import Spider, Request, Response

class BasicSpider(Spider):
    name = "basic_spider"
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response: Response) -> Any:
        # Extract quotes
        for quote in response.root.xpath("//div[@class='quote']"):
            text = quote.xpath("./span[@class='text']/text()")[0]
            author = quote.xpath("./span/small[@class='author']/text()")[0]

            yield {
                "text": text,
                "author": author
            }

        # Follow pagination
        next_page = response.root.xpath("//li[@class='next']/a/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )

if __name__ == "__main__":
    BasicSpider.start()
```

## E-commerce Scraper

A spider that crawls an e-commerce website and extracts product information.

```python
from typing import Any
from smallder import Spider, Request, Response

class EcommerceSpider(Spider):
    name = "ecommerce_spider"
    start_urls = ["https://example-ecommerce.com/products"]

    def parse(self, response: Response) -> Any:
        # Extract product links
        for product_link in response.root.xpath("//div[@class='product']/a/@href"):
            yield Request(
                url=response.urljoin(product_link),
                callback=self.parse_product
            )

        # Follow pagination
        next_page = response.root.xpath("//a[@class='next-page']/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )

    def parse_product(self, response: Response) -> Any:
        # Extract product details
        product = {
            "url": response.url,
            "name": response.root.xpath("//h1[@class='product-name']/text()")[0].strip(),
            "price": response.root.xpath("//span[@class='price']/text()")[0].strip(),
            "description": "".join(response.root.xpath("//div[@class='description']//text()")).strip()
        }

        # Extract images
        images = response.root.xpath("//div[@class='product-images']//img/@src")
        product["images"] = [response.urljoin(img) for img in images]

        yield product

if __name__ == "__main__":
    EcommerceSpider.start()
```

## API Scraper

A spider that interacts with a JSON API.

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

        # Extract items
        for item in data["items"]:
            yield {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"]
            }

        # Follow pagination
        if data["has_next_page"]:
            next_page = data["next_page_url"]
            yield Request(
                url=next_page,
                callback=self.parse
            )

if __name__ == "__main__":
    ApiSpider.start()
```

## Login and Session Handling

A spider that logs in to a website and maintains a session.

```python
from typing import Any
from smallder import Spider, Request, Response

class LoginSpider(Spider):
    name = "login_spider"
    start_urls = ["https://example.com/login"]

    def parse(self, response: Response) -> Any:
        # Extract CSRF token
        csrf_token = response.root.xpath("//input[@name='csrf_token']/@value")[0]

        # Submit login form
        yield Request(
            url="https://example.com/login",
            method="POST",
            data={
                "username": "your_username",
                "password": "your_password",
                "csrf_token": csrf_token
            },
            callback=self.after_login,
            dont_filter=True  # Don't filter out this URL even though we've seen it before
        )

    def after_login(self, response: Response) -> Any:
        # Check if login was successful
        if "Welcome" in response.text:
            self.log.info("Login successful!")

            # Visit protected page
            yield Request(
                url="https://example.com/protected-area",
                callback=self.parse_protected
            )
        else:
            self.log.error("Login failed!")

    def parse_protected(self, response: Response) -> Any:
        # Extract data from protected page
        yield {
            "url": response.url,
            "title": response.root.xpath("//title/text()")[0]
        }

if __name__ == "__main__":
    LoginSpider.start()
```

## Distributed Crawler with Redis

A spider that uses Redis for distributed crawling.

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
        # Convert Redis data to Request objects
        url = data.decode('utf-8')
        return Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> Any:
        # Extract data
        title = response.root.xpath("//title/text()")[0]

        yield {
            "url": response.url,
            "title": title
        }

        # Extract links
        for link in response.root.xpath("//a/@href"):
            full_url = response.urljoin(link)
            yield Request(url=full_url, callback=self.parse)

if __name__ == "__main__":
    DistributedSpider.start()
```

To add URLs to the Redis queue:

```python
import redis
r = redis.StrictRedis.from_url("redis://localhost:6379/0")
r.lpush("distributed_spider:tasks", "https://example.com")
```

## Database Integration

A spider that stores data in a MySQL database.

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
        # Extract quotes
        for quote in response.root.xpath("//div[@class='quote']"):
            text = quote.xpath("./span[@class='text']/text()")[0]
            author = quote.xpath("./span/small[@class='author']/text()")[0]

            yield {
                "text": text,
                "author": author
            }

        # Follow pagination
        next_page = response.root.xpath("//li[@class='next']/a/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )

    def pipline(self, item):
        # Store item in MySQL
        if self.mysql_server:
            with self.mysql_server.connect() as connection:
                connection.execute(
                    "INSERT INTO quotes (text, author) VALUES (:text, :author)",
                    item
                )

if __name__ == "__main__":
    DatabaseSpider.start()
```

## Custom Middleware

A spider with custom middleware for handling cookies and headers.

```python
# middleware/custom.py
class CookieMiddleware:
    def __init__(self, spider):
        self.spider = spider

    def process_request(self, request):
        # Add cookies to all requests
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
        # Rotate user agents
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

## Error Handling

A spider with custom error handling.

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
            # Don't retry 404 errors
            raise DiscardException(f"Page not found: {response.url}")

        if response.status_code == 500:
            # Force a retry for 500 errors
            raise RetryException(f"Server error: {response.url}")

        # Process successful response
        yield {
            "url": response.url,
            "status": response.status_code
        }

    def error_callback(self, failure):
        # Log the error
        self.log.error(f"Error processing {failure.request.url}: {failure.exception}")

        if isinstance(failure.exception, RequestException):
            # Connection error, DNS failure, etc.
            self.log.error(f"Request exception: {failure.exception}")

        # Return the exception to allow normal error handling
        return failure.exception

if __name__ == "__main__":
    ErrorHandlingSpider.start()
```

## Custom Request Fetching

A spider with a custom fetch method for specific requests.

```python
from typing import Any
import json
from smallder import Spider, Request, Response

class CustomFetchSpider(Spider):
    name = "custom_fetch_spider"
    start_urls = ["https://example.com"]

    def custom_fetch(self, request):
        # Simulate a response without making an actual HTTP request
        if "api" in request.url:
            content = json.dumps({
                "items": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ]
            }).encode('utf-8')

            return Response(
                url=request.url,
                status_code=200,
                content=content,
                request=request
            )

        # For other URLs, use the default fetch method
        return None

    def parse(self, response: Response) -> Any:
        # Extract links
        for link in response.root.xpath("//a/@href"):
            full_url = response.urljoin(link)

            # Use custom fetch for API URLs
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
        # Process API response
        data = response.json()

        for item in data["items"]:
            yield {
                "id": item["id"],
                "name": item["name"]
            }

if __name__ == "__main__":
    CustomFetchSpider.start()
```

## Batch Processing

A spider that processes items in batches.

```python
from typing import Any
from smallder import Spider, Request, Response

class BatchSpider(Spider):
    name = "batch_spider"
    start_urls = ["https://quotes.toscrape.com/"]

    # Enable batch processing
    pipline_mode = "list"
    pipline_batch = 10  # Process items in batches of 10

    def parse(self, response: Response) -> Any:
        # Extract quotes
        for quote in response.root.xpath("//div[@class='quote']"):
            text = quote.xpath("./span[@class='text']/text()")[0]
            author = quote.xpath("./span/small[@class='author']/text()")[0]

            yield {
                "text": text,
                "author": author
            }

        # Follow pagination
        next_page = response.root.xpath("//li[@class='next']/a/@href")
        if next_page:
            yield Request(
                url=response.urljoin(next_page[0]),
                callback=self.parse
            )

    def pipline(self, items):
        # Process a batch of items
        if not items:
            return

        self.log.info(f"Processing batch of {len(items)} items")

        # Example: Write to a file
        with open("quotes.jsonl", "a") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    BatchSpider.start()
```

## Passing Parameters to Spider

A spider that accepts parameters when started.

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
        # Extract items
        for item in response.root.xpath("//div[@class='item']"):
            name = item.xpath("./h2/text()")[0]
            price = item.xpath("./span[@class='price']/text()")[0]

            yield {
                "category": self.category,
                "name": name,
                "price": price
            }

if __name__ == "__main__":
    # Pass parameters to the spider
    ParameterizedSpider.start(category="electronics", pages=3)
```

## Using cURL Commands

A spider that creates requests from cURL commands.

```python
from typing import Any
from smallder import Spider, Request, Response

class CurlSpider(Spider):
    name = "curl_spider"

    def start_requests(self):
        # Create a request from a cURL command
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

        # If there's a next page, create another request from cURL
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
