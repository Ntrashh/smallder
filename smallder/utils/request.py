import functools
import hashlib
import json
import time
from typing import Iterable, Optional, Tuple, Union
from weakref import WeakKeyDictionary
from w3lib.url import canonicalize_url

from smallder import Request


def to_unicode(
        text: Union[str, bytes], encoding: Optional[str] = None, errors: str = "strict"
) -> str:
    """Return the unicode representation of a bytes object ``text``. If
    ``text`` is already an unicode object, return it as-is."""
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError(
            "to_unicode must receive a bytes or str "
            f"object, got {type(text).__name__}"
        )
    if encoding is None:
        encoding = "utf-8"
    return text.decode(encoding, errors)


def to_bytes(
        text: Union[str, bytes], encoding: Optional[str] = None, errors: str = "strict"
) -> bytes:
    """Return the binary representation of ``text``. If ``text``
    is already a bytes object, return it as-is."""
    if isinstance(text, bytes):
        return text
    if not isinstance(text, str):
        raise TypeError(
            "to_bytes must receive a str or bytes " f"object, got {type(text).__name__}"
        )
    if encoding is None:
        encoding = "utf-8"
    return text.encode(encoding, errors)


_fingerprint_cache = WeakKeyDictionary()




def process_data(data):
    if isinstance(data, dict):
        return json.dumps(data, sort_keys=True)
    return data or ""

def fingerprint(request, *, include_headers=None, keep_fragments=True):
    processed_include_headers = tuple(
        to_bytes(h.lower()) for h in sorted(include_headers)
    ) if include_headers else None

    cache = _fingerprint_cache.setdefault(request, {})
    cache_key = (processed_include_headers, keep_fragments)

    if cache_key not in cache:
        data = process_data(request.data)
        _json = process_data(request.json)
        params = process_data(request.params)

        fingerprint_data = {
            "method": to_unicode(request.method),
            "url": canonicalize_url(request.url, keep_fragments=keep_fragments),
            "body": data.encode('utf-8').hex(),
            "json": _json.encode('utf-8').hex(),
            "params": params.encode('utf-8').hex(),
        }

        fingerprint_json = json.dumps(fingerprint_data, sort_keys=True)
        cache[cache_key] = hashlib.sha1(fingerprint_json.encode()).digest()

    return cache[cache_key]


def retry(retry_count=3, delay=1, allowed_exceptions=(Exception,)):
    """
    一个用于重试的装饰器。

    :param retry_count: 重试次数
    :param delay: 重试间隔时间（秒）
    :param allowed_exceptions: 允许重试的异常类型
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal retry_count
            attempts = 0
            while attempts < retry_count:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    time.sleep(delay)
                    attempts += 1
            return func(*args, **kwargs)

        return wrapper

    return decorator


def request_from_dict(d: dict, spider):
    """Create a :class:`~scrapy.Request` object from a dict.

    If a spider is given, it will try to resolve the callbacks looking at the
    spider for methods with the same name.
    """
    kwargs = {key: value for key, value in d.items() if key in Request.attributes}
    if d.get("callback") and spider:
        kwargs["callback"] = _get_method(spider, d["callback"])
    if d.get("errback") and spider:
        kwargs["errback"] = _get_method(spider, d["errback"])
    if d.get("fetch") and spider:
        kwargs["fetch"] = _get_method(spider, d["fetch"])
    return Request(**kwargs)


def _get_method(obj, name):
    """Helper function for request_from_dict"""
    name = str(name)
    try:
        return getattr(obj, name)
    except AttributeError:
        raise ValueError(f"Method {name!r} not found in: {obj}")
