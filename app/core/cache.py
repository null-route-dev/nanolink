import json
from typing import Optional, Any
import redis.asyncio as redis
from core.config import settings

redis_client = None

async def get_redis_client() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client

class CacheService:
    def __init__(self):
        self.client = None

    async def _get_client(self) -> redis.Redis:
        if self.client is None:
            self.client = await get_redis_client()
        return self.client

    async def get(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, expire: int = None) -> None:
        client = await self._get_client()
        if expire is None:
            expire = settings.redis_cache_expire_seconds
        await client.set(key, json.dumps(value), ex=expire)

    async def delete(self, key: str) -> None:
        client = await self._get_client()
        await client.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        client = await self._get_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)

    async def exists(self, key: str) -> bool:
        client = await self._get_client()
        return await client.exists(key)

cache_service = CacheService()