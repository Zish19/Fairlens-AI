import json
from typing import Any, Optional
import redis.asyncio as redis
from apps.api.core.config import settings

redis_client = None

async def init_redis():
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()

class CacheService:
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        if not redis_client:
            return None
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    async def set(key: str, value: Any, expire: int = 3600):
        if not redis_client:
            return
        await redis_client.set(key, json.dumps(value), ex=expire)
        
    @staticmethod
    async def delete(key: str):
        if not redis_client:
            return
        await redis_client.delete(key)
