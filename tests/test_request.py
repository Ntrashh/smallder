import pytest
from urllib.parse import urlencode
from smallder import Request  # 请替换为实际的模块名

def test_initialization():
    """测试 Request 类的基本初始化"""
    req = Request(method="get", url="http://example.com", params={"key": "value"})
    assert req.method == "GET"
    assert req.url == "http://example.com"
    assert req.params == {"key": "value"}
    assert req.timeout == 5

def test_full_url():
    """测试full_url方法的URL拼接功能"""
    req = Request(method="get", url="http://example.com", params={"key": "value"})
    expected_url = "http://example.com?" + urlencode({"key": "value"})
    assert req.full_url() == expected_url

def test_replace():
    """测试replace方法，验证是否创建了新的Request实例"""
    req = Request(method="get", url="http://example.com")
    new_req = req.replace(url="http://new-example.com")
    assert req != new_req
    assert new_req.url == "http://new-example.com"
    assert req.url == "http://example.com"

def test_headers_setter():
    """测试 headers setter 方法"""
    req = Request(method="get", url="http://example.com", headers={"User-Agent": "test-agent"})
    assert req.headers["Connection"] == "close"  # 确保 Connection 被添加
    assert req.headers["User-Agent"] == "test-agent"

def test_headers_invalid():
    """测试 headers 设置非法值时是否抛出错误"""
    with pytest.raises(ValueError):
        Request(method="get", url="http://example.com", headers="invalid headers")

def test_from_curl():
    """测试 from_curl 方法"""
    curl_command = 'curl -X GET "http://example.com" -H "User-Agent: test-agent"'
    req = Request.from_curl(curl_command)
    assert req.url == "http://example.com"
    assert req.method == "GET"
    assert req.headers["User-Agent"] == "test-agent"

def test_meta_property():
    """测试 meta 属性是否能正常存取"""
    req = Request(method="get", url="http://example.com", meta={"key": "value"})
    assert req.meta == {"key": "value"}
    req.meta["new_key"] = "new_value"
    assert req.meta["new_key"] == "new_value"

def test_to_dict():
    """测试 to_dict 方法"""
    class Spider:
        def callback_method(self):
            pass

        def errback_method(self):
            pass

    spider = Spider()
    req = Request(method="get", url="http://example.com", callback=spider.callback_method)
    req_dict = req.to_dict(spider)
    assert req_dict["method"] == "GET"
    assert req_dict["url"] == "http://example.com"
    assert req_dict["callback"] == "callback_method"

def test_referer_property():
    """测试 referer 属性是否能正常存取"""
    req = Request(method="get", url="http://example.com", referer="http://referer.com")
    assert req.referer == "http://referer.com"


