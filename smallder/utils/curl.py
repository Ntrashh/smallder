# -*- coding: utf-8 -*-
import argparse
import json
import re
import shlex
import sys
from collections import OrderedDict, namedtuple
from urllib.parse import parse_qsl
from six.moves import http_cookies as Cookie

parser = argparse.ArgumentParser()
parser.add_argument('command')
parser.add_argument('url')
parser.add_argument('-d', '--data')
parser.add_argument('-b', '--data-binary', '--data-raw', default=None)
parser.add_argument('-X', default='')
parser.add_argument('-H', '--header', action='append', default=[])
parser.add_argument('--compressed', action='store_true')
parser.add_argument('-k', '--insecure', action='store_true')
parser.add_argument('--user', '-u', default=())
parser.add_argument('-i', '--include', action='store_true')
parser.add_argument('-s', '--silent', action='store_true')
parser.add_argument('-x', '--proxy', default={})
parser.add_argument('-U', '--proxy-user', default='')

BASE_INDENT = " " * 4

ParsedContext = namedtuple('ParsedContext', ['method', 'url', 'data', 'headers', 'cookies', 'verify', 'auth', 'proxy'])


def normalize_newlines(multiline_text):
    return multiline_text.replace(" \\\n", " ")


def parse_context(curl_command):
    method = "get"

    tokens = shlex.split(normalize_newlines(curl_command)) or []
    try:
        parsed_args = parser.parse_args(tokens)
    except SystemExit:
        raise ValueError("curl_command 不能为空")

    post_data = parsed_args.data or parsed_args.data_binary
    if post_data:
        method = 'post'

    if parsed_args.X:
        method = parsed_args.X.lower()

    cookie_dict = OrderedDict()
    quoted_headers = OrderedDict()

    for curl_header in parsed_args.header:
        if curl_header.startswith(':'):
            occurrence = [m.start() for m in re.finditer(':', curl_header)]
            header_key, header_value = curl_header[:occurrence[1]], curl_header[occurrence[1] + 1:]
        else:
            if len(curl_header.split(":", 1)) != 2:
                continue
            header_key, header_value = curl_header.split(":", 1)

        if header_key.lower().strip("$") == 'cookie':
            cookie = Cookie.SimpleCookie(bytes(header_value, "ascii").decode("unicode-escape"))
            for key in cookie:
                cookie_dict[key] = cookie[key].value
        else:
            quoted_headers[header_key] = header_value.strip()

    # add auth
    user = parsed_args.user
    if parsed_args.user:
        user = tuple(user.split(':'))

    # add proxy and its authentication if it's available.
    proxies = parsed_args.proxy
    # proxy_auth = parsed_args.proxy_user
    if parsed_args.proxy and parsed_args.proxy_user:
        proxies = {
            "http": "http://{}@{}/".format(parsed_args.proxy_user, parsed_args.proxy),
            "https": "http://{}@{}/".format(parsed_args.proxy_user, parsed_args.proxy),
        }
    elif parsed_args.proxy:
        proxies = {
            "http": "http://{}/".format(parsed_args.proxy),
            "https": "http://{}/".format(parsed_args.proxy),
        }

    return ParsedContext(
        method=method,
        url=parsed_args.url,
        data=post_data,
        headers=quoted_headers,
        cookies=cookie_dict,
        verify=parsed_args.insecure,
        auth=user,
        proxy=proxies,
    )


def curl_to_request_kwargs(curl_command, **kargs):
    try:
        curl_args = shlex.split(curl_command)

        if curl_args[0] != "curl":
            raise ValueError('A curl command must start with "curl"')
        parsed_context = parse_context(curl_command)

        formatter = {
            'method': parsed_context.method,
            'url': parsed_context.url,
            'data': dict_to_pretty_string(parsed_context.data),
            'headers': dict(parsed_context.headers),
            # 在curl中不允许出现cookie
            # 'cookies': dict(parsed_context.cookies),
        }
        return formatter
    except Exception as e:
        raise Exception(e)




def dict_to_pretty_string(the_dict, indent=4):
    if not the_dict:
        return {}
    if isinstance(the_dict, dict):
        return json.dumps(the_dict, sort_keys=True, indent=indent, separators=(',', ': '))
    if isinstance(the_dict,str):
        if the_dict[0] == "{" and the_dict[-1] == "}":
            return the_dict
    try:
        the_dict = json.loads(the_dict)
        return json.dumps(the_dict, sort_keys=True, indent=indent, separators=(',', ': '))
    except json.decoder.JSONDecodeError:
        parsed_result = {}
        pairs = parse_qsl(the_dict, keep_blank_values=True, strict_parsing=True)
        for name, value in pairs:
            parsed_result[name] = value
        return parsed_result
