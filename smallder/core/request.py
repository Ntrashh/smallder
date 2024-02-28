import inspect
from typing import Tuple

from smallder.utils.curl import curl_to_request_kwargs


class Request:
    attributes: Tuple[str, ...] = (
        "url",
        "callback",
        "method",
        "headers",
        "data",
        "cookies",
        "meta",
        "proxies",
        # "encoding",
        # "priority",
        "dont_filter",
        "referer",
        "verify",
        "allow_redirects",
        # "errback",
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
            cookies=None,
            timeout=5,
            callback="parse",
            meta=None,
            referer=None,
            proxies=None,
            dont_filter=False,
            verify=False,
            allow_redirects=False,
    ):
        self.method = "POST" if method.upper() == "POST" or data and data != "{}" else "GET"
        self.url = url
        self.params = params
        self.headers = headers
        self.data = data
        self.cookies = cookies
        self.timeout = timeout
        self.callback = callback
        self.proxies = proxies
        self.dont_filter = dont_filter
        self.verify = verify
        self.allow_redirects = allow_redirects
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

    @classmethod
    def from_curl(cls,
                  curl_command: str,
                  **kwargs, ):
        request_kwargs = curl_to_request_kwargs(curl_command)
        request_kwargs.update(kwargs)
        return cls(**request_kwargs)

    def __str__(self):
        parts = ["Request("]
        if self.method is not None:
            parts.append(f"    method = '{self.method}',")

        if self.url is not None:
            parts.append(f"    url = '{self.url}',")

        if self.params is not None:
            parts.append(f"    params = {self.params},")

        if self.data is not None:
            parts.append(f"    data = {self.data},")

        if self.cookies is not None:
            parts.append(f"    cookies = {self.cookies},")

        callback_name = self.callback.__name__ if self.callback else "None"
        parts.append(f"    callback = {callback_name}")

        parts.append(")")

        return "\n".join(parts)

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
