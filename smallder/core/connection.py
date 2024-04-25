from urllib.parse import urlparse

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
        f'mysql+pymysql://{parsed_url.username}:{parsed_url.password}@{parsed_url.hostname}:{parsed_url.port}/{parsed_url.path.lstrip("/")}',
        echo=True,  # 打印SQL语句，便于调试
        pool_size=100,
        max_overflow=100
    )
    return engine
