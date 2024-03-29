import importlib
import time
from typing import Any, Dict
from smallder.utils.utils import singleton
StatsT = Dict[str, Any]


class StatsCollector:
    def __init__(self):
        self._stats: StatsT = {}
        self._start_time = time.time()
        # self.spider = spider

    def handler(self, func):
        stats_mapping = {
            "process_request": "request",
            "process_response": "response",  # assuming the second condition was meant for 'process_response'
            "process_item": "item"
        }

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            key = stats_mapping.get(func.__name__)
            if key == "response":
                response = args[1]
                status_code_key = f"status_code_{response.status_code}"
                self.inc_value(status_code_key)
            _r = args[1]
            if getattr(_r, "retry", 0) > 0:
                return result
            self.inc_value(key)
            return result

        return wrapper

    def get_value(

            self, key: str, default: Any = None) -> Any:
        return self._stats.get(key, default)

    def get_stats(self) -> StatsT:
        return self._stats

    def set_value(self, key: str, value: Any) -> None:
        self._stats[key] = value

    def set_stats(self, stats: StatsT) -> None:
        self._stats = stats

    def inc_value(
            self, key: str, count: int = 1, start: int = 0
    ) -> None:
        d = self._stats
        d[key] = d.setdefault(key, start) + count

    def max_value(self, key: str, value: Any) -> None:
        self._stats[key] = max(self._stats.setdefault(key, value), value)

    def min_value(self, key: str, value: Any) -> None:
        self._stats[key] = min(self._stats.setdefault(key, value), value)

    def clear_stats(self) -> None:
        self._stats.clear()

    def _persist_stats(self, stats: StatsT, spider) -> None:
        pass

    def on_spider_stopped(self, sender, **kwargs):
        # 处理爬虫停止信号
        self.set_value("time", time.time() - self._start_time)


@singleton
class MemoryStatsCollector(StatsCollector):
    def __init__(self):
        super().__init__()
        self.spider_stats: Dict[str, StatsT] = {}

    def _persist_stats(self, stats: StatsT, spider) -> None:
        self.spider_stats[spider.name] = stats


# class StatsCollectorFactory:
#     @classmethod
#     def create_stats_collector(cls, spider):
#
#         stats_collect = cls.load_filter(spider)
#         if stats_collect is None:
#             return StatsCollector(spider)
#         else:
#             return stats_collect(spider)
#
#     @classmethod
#     def load_filter(cls, spider):
#         mw_path = spider.custom_settings.get("stats_collector_class", "")
#         if not mw_path:
#             return
#         try:
#             module_path, class_name = mw_path.rsplit('.', 1)
#             module = importlib.import_module(module_path)
#             return getattr(module, class_name)
#         except (ImportError, AttributeError) as e:
#             spider.log.error(f"Failed to load stats_collector_class class {mw_path}: {e}")
#             return None
