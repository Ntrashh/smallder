import json
from json import JSONDecodeError
from urllib.parse import urljoin
from lxml import etree

import chardet
from smallder.utils.utils import guess_json_utf


class Response:
    attributes = [
        "url",
        "status_code",
        # "headers",
        "content",
        # "flags",
        "request",
        "encoding",
        "cookies",
        "elapsed"
        # "ip_address",
        # "protocol",
    ]

    def __init__(self, url=None, status_code=200, content=None, request=None, encoding="utf-8", cookies=None,
                 elapsed=0):
        self.url = url
        self.content = content
        self.request = request
        self.status_code = status_code
        self.encoding = encoding
        self.cookies = cookies or {}
        self.elapsed = elapsed

    def __repr__(self):
        parts = ["<Response"]
        if self.status_code is not None:
            parts.append(f" status_code = {self.status_code},")

        if self.url is not None:
            parts.append(f" url = '{self.url}'")

        if self.referer:
            parts.append(f" referer = '{self.referer}'")

        parts.append(">")

        return "".join(parts)

    @property
    def meta(self):
        try:
            return self.request.meta
        except AttributeError:
            raise AttributeError(
                "Response.meta not available, this response "
                "is not tied to any request"
            )

    @property
    def referer(self):
        try:
            return self.request.referer
        except AttributeError:
            raise AttributeError(
                "Response.referer not available, this response "
                "is not tied to any request"
            )

    @property
    def text(self, encoding="utf-8"):
        try:
            return self.content.decode(encoding)
        except UnicodeDecodeError:
            try:
                encoding = self._auto_char_code() or "utf-8"
                return self.content.decode(encoding, errors="ignore")
            except UnicodeDecodeError:
                raise UnicodeDecodeError(f"{encoding} codec can't decode")
            except TypeError:
                raise UnicodeDecodeError("codec can't decode")

    @property
    def ok(self):
        return self.status_code == 200

    def _auto_char_code(self):
        char_code = chardet.detect(self.content)
        encoding = char_code.get('encoding', 'utf-8')
        return encoding

    def urljoin(self, url):

        return urljoin(self.url, url)

    def json(self, **kwargs):
        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using charset_normalizer to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return json.loads(self.content.decode(encoding), **kwargs)
                except JSONDecodeError as e:
                    raise JSONDecodeError(e.msg, e.doc, e.pos)

        try:
            return json.loads(self.text, **kwargs)
        except JSONDecodeError as e:
            raise JSONDecodeError(e.msg, e.doc, e.pos)

    def replace(self, *args, **kwargs):
        """Create a new Response with the same attributes except for those given new values"""
        for x in self.attributes:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop("cls", self.__class__)
        return cls(*args, **kwargs)

    @property
    def root(self):
        return etree.HTML(self.text)
