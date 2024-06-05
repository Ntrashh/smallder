from urllib.parse import urlparse, quote

import redis
from sqlalchemy import create_engine


def from_redis_setting(redis_url):
    """
    redis://:yourpassword@localhost:6379/0
    redis://localhost:6379/0
    """
    return redis.StrictRedis.from_url(redis_url)


def from_mysql_setting(mysql_url):
    if not mysql_url:
        return
    # 解析数据库URL
    parsed_url = urlparse(mysql_url)
    engine = create_engine(
        f'mysql+pymysql://{quote(parsed_url.username)}:{quote(parsed_url.password)}@{parsed_url.hostname}:{parsed_url.port}/{parsed_url.path.lstrip("/")}',
        echo=False,  # 打印SQL语句，便于调试
        pool_size=100,
        max_overflow=20,  # 允许最大溢出连接数为 20
        pool_timeout=30,  # 设置获取连接的超时时间为 30 秒
        pool_recycle=1800,  # 每 1800 秒回收连接（即 30 分钟）
        pool_pre_ping=True  # 启用连接可用性检测
    )
    return engine
