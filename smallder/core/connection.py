import redis


def from_setting(redis_url):
    """
    redis://:yourpassword@localhost:6379/0
    redis://localhost:6379/0
    """
    return redis.StrictRedis.from_url(redis_url)
