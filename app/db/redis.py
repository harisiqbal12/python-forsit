import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

redis_client_sub = redis.from_url(settings.REDIS_URL)


def get_redis() -> redis.Redis:
    return redis_client


def get_redis_sub() -> redis.Redis:
    return redis_client_sub
