import time
from typing import Any, Dict

from smallder.utils.utils import singleton

StatsT = Dict[str, Any]


class StatsCollector:
    def __init__(self, spider):
        self._stats: StatsT = {}
        self._cache_stats = {}
        self._start_time = time.time()
        self.start_period = time.time()
        self.spider = spider

    def handler(self, task=None):
        if task is not None:
            cls_name = type(task).__name__.lower()
            if cls_name == "response":
                status_code_key = f"status_code_{task.status_code}"
                self.inc_value(status_code_key)
            if isinstance(task, str):
                cls_name = task
            self.inc_value(cls_name)
        if time.time() - self.start_period > 60:
            log_str = [f"任务池数量 : {len(self.spider.futures)}"]
            for key, value in self._cache_stats.items():
                log_str.append(f"{key} : {value}/min")
            self.spider.log.info("  ".join(log_str))
            self._cache_stats.clear()
            self.start_period = time.time()

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
        self._cache_stats[key] = self._cache_stats.setdefault(key, start) + count

    def max_value(self, key: str, value: Any) -> None:
        self._stats[key] = max(self._stats.setdefault(key, value), value)

    def min_value(self, key: str, value: Any) -> None:
        self._stats[key] = min(self._stats.setdefault(key, value), value)

    def clear_stats(self) -> None:
        self._stats.clear()

    def _persist_stats(self, stats: StatsT, spider) -> None:
        pass

    def on_spider_start(self, sender, **kwargs) -> None:
        self._start_time = time.time()

    def on_spider_stopped(self, sender, **kwargs):
        # 处理爬虫停止信号
        self.set_value("time", time.time() - self._start_time)


@singleton
class MemoryStatsCollector(StatsCollector):

    def __init__(self, spider):
        super().__init__(spider)

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
