import os
import re
import sys
from smallder.core.request import Request
from smallder.core.response import Response
from smallder.core.spider import Spider

sys.path.insert(0, re.sub(r"([\\/]items)|([\\/]spiders)", "", os.getcwd()))


__all__ = [
    "Spider",
    "Request",
    "Response",
]

__version__ = "0.1.0"