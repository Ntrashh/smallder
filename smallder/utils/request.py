import functools
import hashlib
import json
import time
from typing import Iterable, Optional, Tuple, Union
from weakref import WeakKeyDictionary
from w3lib.url import canonicalize_url



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


def fingerprint(
        request,
        *,
        include_headers: Optional[Iterable[Union[bytes, str]]] = None,
        keep_fragments: bool = False,
) -> bytes:
    processed_include_headers: Optional[Tuple[bytes, ...]] = None
    if include_headers:
        processed_include_headers = tuple(
            to_bytes(h.lower()) for h in sorted(include_headers)
        )
    cache = _fingerprint_cache.setdefault(request, {})
    cache_key = (processed_include_headers, keep_fragments)
    if cache_key not in cache:
        # To decode bytes reliably (JSON does not support bytes), regardless of
        # character encoding, we use bytes.hex()

        if isinstance(request.data, dict):
            data = json.dumps(request.data)
        elif request.data is None:
            data = ""
        else:
            data = request.data
        fingerprint_data = {
            "method": to_unicode(request.method),
            "url": canonicalize_url(request.url, keep_fragments=keep_fragments),
            "body": (data.encode() or b"").hex(),
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