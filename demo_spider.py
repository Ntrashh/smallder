import copy
import time
from pathlib import Path
from random import random, randint
from typing import Any
from urllib.parse import urlparse, parse_qsl
from smallder import Spider, Request, Response



class IconfontSpider(Spider):
    name = "iconfont_spider"
    fastapi = False  # 控制内部统计api的数据
    redis_task_key = ""  # 任务池key如果存在值,则直接从redis中去任务,需要重写make_request_for_redis
    start_urls = []
    max_retry: int = 1  # 重试次数
    # thread_count = 1  # 线程总数 默认为cpu核心数两倍线程
    # batch_size = 0         # 批次从redis中获取多少数据 不使用redis不需要次参数
    # pipline_mode = "list"  # 两种模式 single代表单条入库,list代表多条入库 默认为single
    # pipline_batch = 100    # 只有在pipline_mode=list时生效,代表多少条item进入pipline,默认100
    # save_failed_request = False  # 保存错误请求到redis,不使用redis可不用开启
    custom_settings = {
        # "middleware_settings": {}, # 设置中间件
        # "mysql": "",  # "mysql://xxx:xxxxx@host:port/db_name"
        # "redis": "" # "redis://xxx:xxxxx@host:port/db_name"
    }

    def __init__(self, url, name):
        self.start_url = url
        self.name = name

    def start_requests(self):
        yield Request(url=self.start_url, callback=self.parse)

    def fetch(self,request):
        return Response(content=b"",status_code=200,request=request)

    def parse(self, response: Response) -> Any:
        response_json = response.json()
        data = response_json.get("data", {})
        lists = data.get("lists", [])

        count = data.get("count", 0)

        # 解析 URL 查询参数
        parsed_url = urlparse(response.url)
        params_list = parse_qsl(parsed_url.query)

        # 转换为字典
        params_dict = dict(params_list)

        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        # for _list in lists:
        #     _id = _list.get("id", 0)
        #     yield Request(
        #         url=f"https://www.iconfont.cn/api/collection/detail.json?id={_id}&t=1737094944589",
        #         callback=self.detail_parse
        #     )
        #
        # page = count // 9 if count % 9 == 0 else count // 9 + 1
        # if int(params_dict.get("page",0)) == 1:
        #     for i in range(2, page + 1):
        #         params = copy.copy(params_dict)
        #         params["page"] = str(i)
        #         yield Request(url=url, params=params, callback=self.parse)

    def detail_parse(self, response: Response) -> Any:
        response_json = response.json()
        data = response_json.get("data", {})
        collection = data.get("collection", {})
        creator = data.get("creator", {})
        project_name = collection.get("name", "")
        nike_name = creator.get("nickname", "")
        fees = collection.get("fees", "")
        tag_type = "公开访问"
        if fees == "free":
            tag_type = "免费使用"
        elif fees == "charge":
            tag_type = "付费使用"
        icons = data.get("icons", [])
        for icon in icons:
            _id = icon.get("id", 0)
            meta = {
                "project_name": project_name,
                "nike_name": nike_name,
                "tage_type": tag_type
            }
            yield Request(
                url=f"https://www.iconfont.cn/api/icon/iconInfo.json?id={_id}&pid=&cid=&t=1737097695671",
                meta=meta,
                callback=self.icon_info_parse
            )

    def icon_info_parse(self, response: Response) -> Any:
        meta = response.meta
        response_json = response.json()
        data = response_json.get("data", {})
        name = data.get("name", "")
        show_svg = data.get("show_svg", "")

    def download_middleware(self, request: Request) -> Request:
        request.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.5.28',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.iconfont.cn/collections/index?spm=a313x.home_index.i3.5.14343a81eUcAZU&type=2&page=1',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        return request


if __name__ == "__main__":
    IconfontSpider.start(name="多色图标库",
                         url="https://www.iconfont.cn/api/collections.json?type=2&sort=time&limit=9&page=1&keyword=&t=1737096559247")
