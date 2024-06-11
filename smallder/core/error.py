#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：dfb-spider 
@File    ：error.py
@Author  ：1mnoi
@Date    ：2024/1/8 14:43 
"""


class FetchError(Exception):
    pass


class DiscardException(Exception):
    """
    raise DiscardException discard request or response
    """
    pass


class RetryException(Exception):
    """
    raise RetryException discard request or response
    """
    pass
