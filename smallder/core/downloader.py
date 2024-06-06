from requests.adapters import HTTPAdapter
from urllib3 import Retry
from smallder import Request, Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests

# 禁用SSL证书验证警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Downloader:

    def __init__(self, spider):
        self.spider = spider

    @classmethod
    def fetch(cls, request: Request, retry_time: int = 3):
        """
        @param retry_time:
        @type request: Request
        """
        retries = Retry(
            total=retry_time,
            backoff_factor=0.1,
        )
        with requests.Session() as session:
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))

            with session.request(
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
                                cookies=response.cookies.get_dict(), elapsed=response.elapsed)

    def download(self, request: Request):
        if request.fetch:
            response = request.fetch(request)
        else:
            response = self.fetch(request)
        return response
