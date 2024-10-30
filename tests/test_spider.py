import inspect
import unittest

from smallder import Spider


class SpiderTest(unittest.TestCase):
    spider_class = Spider

    def test_start_requests(self):
        spider = self.spider_class()
        start_requests = spider.start_requests()
        spider.start_urls = ["www.baidu.com"]
        self.assertTrue(inspect.isgenerator(start_requests))
        self.assertEqual(len(list(start_requests)), 1)




