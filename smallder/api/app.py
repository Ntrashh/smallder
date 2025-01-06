from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from smallder.core.statscollectors import MemoryStatsCollector
import uvicorn
import threading


class FastAPIWrapper:
    def __init__(self, host="0.0.0.0", port=8000, spider=None):
        # self.app = FastAPI()
        self.app = Starlette(debug=True, routes=[
            Route('/status', self.get_status, methods=["GET"]),
            Route('/running', self.running, methods=["GET"]),
        ])
        self.host = host
        self.port = port
        self._status = MemoryStatsCollector(spider)

    async def get_status(self, request):
        # 调用启动爬虫的逻辑
        return JSONResponse(
            content={
                "message": "success",
                "data": self._status.get_stats()
            }
        )

    async def running(self, request):
        return JSONResponse(
            content={
                "message": "success",
                "data": "running"
            }
        )

    def run(self):
        threading.Thread(target=uvicorn.run, args=(self.app,),
                         kwargs={'host': self.host, 'port': self.port,"log_level": "critical"},
                         daemon=True, ).start()
