import json
import time
import traceback
from typing import Any, Dict

from loguru import logger

from smallder.utils.utils import singleton

StatsT = Dict[str, Any]


class StatsCollector:
    def __init__(self):
        self._stats: StatsT = {}
        self._start_time = time.time()

    def handler(self, func):
        stats_mapping = {
            "process_request": "request",
            "process_response": "response",  # assuming the second condition was meant for 'process_response'
            "process_item": "item"
        }

        def wrapper(*args, **kwargs):
            key = stats_mapping.get(func.__name__)
            if key == "response":
                response = args[1]
                status_code_key = f"status_code_{response.status_code}"
                self.inc_value(status_code_key)
            self.inc_value(key)
            result = func(*args, **kwargs)
            # And any post-processing after the function call
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
        logger.success(f"Spider Close : {json.dumps(self.get_stats(), ensure_ascii=False, indent=4)}")


@singleton
class MemoryStatsCollector(StatsCollector):
    def __init__(self):
        super().__init__()
        self.spider_stats: Dict[str, StatsT] = {}

    def _persist_stats(self, stats: StatsT, spider) -> None:
        self.spider_stats[spider.name] = stats
