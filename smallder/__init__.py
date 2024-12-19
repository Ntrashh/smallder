import os
import re
import sys

from smallder.core.item import Item
from smallder.core.request import Request
from smallder.core.response import Response
from smallder.core.spider import Spider
from smallder.core.downloader import Downloader
from smallder.core.error import DiscardException,RetryException

sys.path.insert(0, re.sub(r"([\\/]items)|([\\/]spiders)", "", os.getcwd()))

__all__ = [
    "Spider",
    "Request",
    "Response",
    "Item",
    "Downloader"
]

__version__ = "0.0.1"
