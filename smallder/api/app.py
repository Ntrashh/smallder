import threading
from typing import Any, Dict
from fastapi import FastAPI
import uvicorn

from smallder.core.statscollectors import MemoryStatsCollector


class FastAPIWrapper:
    def __init__(self, host="0.0.0.0", port=8000, spider=None):
        self.app = FastAPI()
        self.host = host
        self.port = port
        self._status = MemoryStatsCollector(spider)
        # 将路由添加到FastAPI应用
        self.app.add_api_route("/status", self.get_status, methods=["GET"])
        self.app.add_api_route("/running", self.running, methods=["GET"])

    def get_status(self):
        # 调用启动爬虫的逻辑
        return self.format_response(data=self._status.get_stats(), message="success")

    def running(self):
        return self.format_response(data="running", message="success")

    @staticmethod
    def format_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
        return {
            "success": success,
            "message": message,
            "data": data
        }

    def run(self):
        threading.Thread(target=uvicorn.run, args=(self.app,),
                         kwargs={'host': self.host, 'port': self.port, "log_level": "critical"},
                         daemon=True, ).start()
