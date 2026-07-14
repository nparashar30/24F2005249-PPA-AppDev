import json
import redis
from config import Config

_redis_client = None


def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
    return _redis_client


def cache_get(key):
    try:
        r = get_redis()
        val = r.get(key)
        return json.loads(val) if val else None
    except redis.RedisError:
        return None


def cache_set(key, value, ttl=None):
    try:
        r = get_redis()
        ttl = ttl or Config.CACHE_DEFAULT_TTL
        r.setex(key, ttl, json.dumps(value, default=str))
        return True
    except redis.RedisError:
        return False


def cache_delete(key):
    try:
        r = get_redis()
        r.delete(key)
        return True
    except redis.RedisError:
        return False


def cache_delete_pattern(pattern):
    try:
        r = get_redis()
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
        return True
    except redis.RedisError:
        return False
