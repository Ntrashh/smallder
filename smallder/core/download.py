from smallder import Request, Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from middleware import custom
import traceback
import requests

from smallder.utils.request import retry

# 禁用SSL证书验证警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Download:

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
        # universal_middleware = UniversalMiddleware(self.spider)
        # request = universal_middleware.request_after(request)
        # custom_middleware = self.load_middleware(request)
        # request = self.download_after(custom_middleware, request)
        response = self.fetch(request)
        # response = universal_middleware.response_before(response)
        # response = self.download_before(custom_middleware, response)
        return response

    def load_middleware(self, request: Request):
        _id = request.meta.get("id", "")
        custom_middleware_name = f"Custom{_id}Middleware"
        try:
            custom_middleware_cls = getattr(custom, custom_middleware_name)
            custom_middleware = custom_middleware_cls(self.spider)
        except AttributeError:
            return None
        return custom_middleware

    def download_after(self, custom_middleware, request: Request):
        if custom_middleware:
            try:
                request = custom_middleware.request_after(request)
            except Exception as e:
                self.spider.log.error(
                    f"website : {request.meta.get('id')}  定制中间件 request_after 出现错误 : {e}"
                )
        return request

    def download_before(self, custom_middleware, response: Response):
        if custom_middleware:
            try:
                response = custom_middleware.response_before(response)
            except Exception as e:
                self.spider.log.error(
                    f"website : {response.request.meta.get('id')}  定制中间件 response_before 出现错误 : {e}")
                traceback.print_exc()
        return response
