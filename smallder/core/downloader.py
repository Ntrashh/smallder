from smallder import Request, Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import traceback
import requests

from smallder.utils.request import retry

# 禁用SSL证书验证警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Downloader:

    def __init__(self, spider):
        self.spider = spider

    @classmethod
    @retry(retry_count=3)
    def fetch(cls, request: Request):
        # 假设 'request' 是一个已经定义好的请求对象，包含了必要的属性如method, url等
        with requests.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                data=request.data,
                cookies=request.cookies,
                timeout=request.timeout,
                proxies=request.proxies,
                verify=request.verify,
                allow_redirects=request.allow_redirects,  # 禁止重定向
        ) as response:
            return Response(url=request.url, status_code=response.status_code, content=response.content,
                            request=request,
                            cookies=response.cookies.get_dict())

    def download(self, request: Request):
        response = self.fetch(request)
        return response
