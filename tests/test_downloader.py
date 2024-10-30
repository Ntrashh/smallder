import pytest
from unittest.mock import patch, Mock

from urllib3 import request

from smallder import Request, Response
from smallder import Downloader


@pytest.fixture
def downloader():
    """创建一个示例 Downloader 对象"""
    return Downloader(spider=None)


# # 参数化测试，包含GET和POST请求类型，以及传递参数的不同方式
# @pytest.mark.parametrize("method, params_type, expected_body", [
#     ("GET", None, None),  # GET 请求，不传递任何参数
#     ("POST", "data", {"key": "value"}),  # POST 请求，使用 data 参数
#     ("POST", "json", {"key": "value"}),  # POST 请求，使用 json 参数
# ])
# @patch("requests.Session")
# def test_fetch_with_different_methods(mock_session, method, params_type, expected_body, downloader):
#     """测试 GET 和 POST 请求，data 和 json 参数"""
#     mock_response = Mock()
#     mock_response.status_code = 200
#     mock_response.content = b"response content"
#     mock_response.cookies.get_dict.return_value = {}
#     mock_response.elapsed = 0.1
#     mock_session.return_value.request.return_value.__enter__.return_value = mock_response
#
#     # 构建 Request 对象
#     if params_type == "data":
#         request = Request(method=method, url="http://example.com", data=expected_body)
#     elif params_type == "json":
#         request = Request(method=method, url="http://example.com", json=expected_body)
#     else:
#         request = Request(method=method, url="http://example.com")
#
#     # 执行请求
#     response = downloader.fetch(request)
#
#     # 验证请求被正确构建和发送
#     mock_session.return_value.request.assert_called_once_with(
#         method=method,
#         url="http://example.com",
#         headers=None,
#         params=None,
#         data=expected_body if params_type == "data" else None,
#         json=expected_body if params_type == "json" else None,
#         cookies=None,
#         timeout=5,
#         proxies=None,
#         verify=False,
#         allow_redirects=True
#     )
#
#     # 验证响应
#     assert response.status_code == 200
#     assert response.content == b"response content"
#
#
# # 扩展 download 方法测试，验证针对 GET 和 POST 请求的下载行为
# @pytest.mark.parametrize("method, params_type, expected_body", [
#     ("GET", None, None),
#     ("POST", "data", {"key": "value"}),
#     ("POST", "json", {
#         "data": {
#             "mobile": "y_10403465844",
#             "password": "12345678",
#         },
#         "encrypt": "md5",
#         "etag": "",
#         "id": "1723475390482391",
#         "imei": "0053ef05975d8bd3",
#         "sign": "f1ede67e67df02440aa856240b69ab72",
#         "timestamp": 1723475390482,
#         "user": {
#             "sid": "",
#             "userId": "",
#         },
#     }),
# ])
# @patch("requests.Session")
# def test_download_with_different_methods(mock_session, method, params_type, expected_body, downloader):
#     """测试 download 方法，支持不同请求类型和参数传递方式"""
#     mock_response = Mock()
#     mock_response.status_code = 200
#     mock_response.content = b"response content"
#     mock_response.cookies.get_dict.return_value = {}
#     mock_response.elapsed = 0.1
#     mock_session.return_value.request.return_value.__enter__.return_value = mock_response
#
#     # 构建 Request 对象
#     if params_type == "data":
#         request = Request(method=method, url="https://www.baidu.com", data=expected_body)
#     elif params_type == "json":
#         request = Request(method=method, url="https://app.qianliao.cn/v1/user/mobile-login", json=expected_body)
#     else:
#         request = Request(method=method, url="http://example.com")
#
#     # 执行下载
#     response = downloader.download(request)
#
#     # 验证请求被正确构建和发送
#     mock_session.return_value.request.assert_called_once_with(
#         method=method,
#         url="http://example.com",
#         headers=None,
#         params=None,
#         data=expected_body if params_type == "data" else None,
#         json=expected_body if params_type == "json" else None,
#         cookies=None,
#         timeout=5,
#         proxies=None,
#         verify=False,
#         allow_redirects=True
#     )
#
#     # 验证响应
#     assert response.status_code == 200
#     assert response.content == b"response content"



