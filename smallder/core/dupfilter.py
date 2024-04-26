import importlib
from smallder import Request
from smallder.utils.request import fingerprint


class Filter:

    def request_seen(self, request: Request) -> bool:
        """
        判断请求是否存在如果存在就返回True
        :param request:
        :return:
        """
        pass


class MemoryFilter(Filter):
    fingerprints = set()

    def request_seen(self, request: Request) -> bool:
        fp = fingerprint(request).hex()
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        return False


class RedisFilter(Filter):

    def __init__(self, server, key):
        self.server = server
        self.key = key

    def request_seen(self, request: Request) -> bool:
        fp = fingerprint(request).hex()
        added = self.server.sadd(self.key, fp)
        return added == 0


class FilterFactory:

    @classmethod
    def create_filter(cls, spider):
        server = spider.server
        if server is None:
            _filter = MemoryFilter()
        else:
            _filter_class = cls.load_filter(spider)
            if _filter_class is not None:
                instance = _filter_class(server)
                return instance
            key = f"{spider.name}:dupfilter"
            _filter = RedisFilter(server, key)
        return _filter

    @classmethod
    def load_filter(cls, spider):
        mw_path = spider.custom_settings.get("dupfilter_class", "")
        if not mw_path:
            return
        try:
            module_path, class_name = mw_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            spider.log.error(f"Failed to load middleware class {mw_path}: {e}")
            return None
