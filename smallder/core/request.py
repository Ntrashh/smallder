import inspect
from typing import Tuple
from urllib.parse import urlparse, urlencode, urlunparse

from smallder.utils.curl import curl_to_request_kwargs


class Request:
    attributes: Tuple[str, ...] = (
        "url",
        "callback",
        "method",
        "headers",
        "params",
        "data",
        "json",
        "cookies",
        "meta",
        "timeout",
        "proxies",
        # "encoding",
        "priority",
        "dont_filter",
        "referer",
        "verify",
        "allow_redirects",
        "retry",
        "errback",
        "fetch"
        # "flags",
        # "cb_kwargs",
    )

    def __init__(
            self,
            method="get",
            url=None,
            headers=None,
            params=None,
            data=None,
            json=None,
            cookies=None,
            timeout=5,
            callback=None,
            errback=None,
            meta=None,
            referer=None,
            proxies=None,
            dont_filter=False,
            verify=False,
            allow_redirects=True,
            priority=0,
            fetch=None,
            retry: int = 0  # 控制单个请求的重试次数
    ):
        self.method = "POST" if method.upper() == "POST" or data and data != "{}" else "GET"
        self.url = url
        self.params = params
        self.headers = headers
        self.data = data
        self.json = json
        self.cookies = cookies
        self.timeout = timeout
        self.callback = callback
        self.errback = errback
        self.proxies = proxies
        self.dont_filter = dont_filter
        self.verify = verify
        self.priority = priority
        self.allow_redirects = allow_redirects
        self.retry = retry
        self.fetch = fetch
        self._meta = dict(meta) if meta else None
        self._referer = referer if referer else None

    @property
    def meta(self) -> dict:
        if self._meta is None:
            self._meta = {}
        return self._meta

    @property
    def referer(self) -> str:
        if self._referer is None:
            self._referer = ""
        return self._referer

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        if value is None:
            # 允许headers被显式设置为None
            self._headers = None
        elif isinstance(value, dict):
            # 如果value是字典，则添加"Connection": "close"
            value["Connection"] = "close"
            self._headers = value
        else:
            # 如果value既不是None也不是dict，抛出错误或采取其他处理
            raise ValueError("headers must be a dictionary or None")

    @classmethod
    def from_curl(cls,
                  curl_command: str,
                  **kwargs, ):
        request_kwargs = curl_to_request_kwargs(curl_command)
        request_kwargs.update(kwargs)
        return cls(**request_kwargs)

    def full_url(self):
        """
        返回url拼接params的完整字符串
        """
        params = self.params if self.params else ""
        parsed_url = urlparse(self.url)
        # 将参数字典转换为查询字符串
        query_string = urlencode(params, doseq=True)
        # 创建包含新查询字符串的完整URL
        return urlunparse(parsed_url._replace(query=query_string))

    def __repr__(self):
        parts = ["<Request"]
        if self.method is not None:
            parts.append(f" method = '{self.method}',")

        if self.url is not None:
            parts.append(f" url = '{self.url}',")

        if self.params is not None:
            parts.append(f" params = {self.params},")

        if self.data is not None:
            parts.append(f" data = {self.data},")

        if self.cookies is not None:
            parts.append(f" cookies = {self.cookies},")

        callback_name = self.callback.__name__ if self.callback is not None else "None"
        parts.append(f" callback = {callback_name}")

        parts.append(">")

        return "".join(parts)

    def copy(self) -> "Request":
        return self.replace()

    def replace(self, *args, **kwargs) -> "Request":
        """Create a new Request with the same attributes except for those given new values"""
        for x in self.attributes:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop("cls", self.__class__)
        return cls(*args, **kwargs)

    def to_dict(self, spider):
        d = {
            "method": self.method,
            "url": self.url,  # urls are safe (safe_string_url)
            "headers": self.headers,
            "callback": _find_method(spider, self.callback)
            if callable(self.callback)
            else self.callback,
            "errback": _find_method(spider, self.errback) if callable(self.errback)
            else self.errback,
            "fetch": _find_method(spider, self.fetch) if callable(self.fetch) else self.fetch,
        }
        for attr in self.attributes:
            d.setdefault(attr, getattr(self, attr))
        if type(self) is not Request:  # pylint: disable=unidiomatic-typecheck
            d["_class"] = self.__module__ + "." + self.__class__.__name__
        return d


def _find_method(obj, func):
    """Helper function for Request.to_dict"""
    # Only instance methods contain ``__func__``
    if obj and hasattr(func, "__func__"):
        members = inspect.getmembers(obj, predicate=inspect.ismethod)
        for name, obj_func in members:
            # We need to use __func__ to access the original function object because instance
            # method objects are generated each time attribute is retrieved from instance.
            #
            # Reference: The standard type hierarchy
            # https://docs.python.org/3/reference/datamodel.html
            if obj_func.__func__ is func.__func__:
                return name
    raise ValueError(f"Function {func} is not an instance method in: {obj}")
