# Smaller 一个开箱即用的爬虫框架


## 简介

Smaller 是一个开箱即用的轻量爬虫框架

github地址 : https://github.com/Ntrashh/smallder



### 环境要求
 - Python 3.7.0+
 - Works on Linux, Windows, macOS

### 安装
```cmd
pip3 install smallder
```

### 使用
创建爬虫
```shell
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





如果你在使用过程中对smallder有任何问题或建议可以联系我

微信:


![wechat](https://user-images.githubusercontent.com/109586486/210029580-4bb2f7bb-ed19-4971-ad0a-788aa659e2ff.jpg)

邮箱:
yinghui0214@163.com




##
<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.png" alt="PyCharm logo."  width="30%" >