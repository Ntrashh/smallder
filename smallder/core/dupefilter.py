import importlib

from smallder import Request
from smallder.utils.request import fingerprint
from utils.url import filter_url_params_corrected


class Filter:

    def request_seen(self, request: Request) -> bool:
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

    def create_filter(self, spider):
        server = spider.server
        if server is None:
            _filter = MemoryFilter()
        else:
            _filter_class = self.load_filter(spider)
            if _filter_class is not None:
                instance = _filter_class(server)
                return instance
            key = f"{spider.name}:dupefilter"
            _filter = RedisFilter(server, key)
        return _filter

    def load_filter(self, spider):
        mw_path = spider.custom_settings.get("dupefilter_class","")
        try:
            module_path, class_name = mw_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            spider.log.error(f"Failed to load middleware class {mw_path}: {e}")
            return None
