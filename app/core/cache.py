import json
from typing import Optional, Any

import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError

from core.config import settings

redis_client = None

async def get_redis_client() -> Optional[redis.Redis]:
    global redis_client
    if redis_client is not None:
        return redis_client
    try:
        redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=settings.redis_connect_timeout,
            socket_timeout=settings.redis_read_timeout
        )
        await redis_client.ping()
    except (ConnectionError, TimeoutError, Exception):
        redis_client = None
    return redis_client

class CacheService:
    async def _get_client(self) -> Optional[redis.Redis]:
        return await get_redis_client()

    async def get(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        if client is None:
            return None
        try:
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, expire: int = None) -> None:
        client = await self._get_client()
        if client is None:
            return
        try:
            if expire is None:
                expire = settings.redis_cache_expire_seconds
            await client.set(key, json.dumps(value), ex=expire)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        client = await self._get_client()
        if client is None:
            return
        try:
            await client.delete(key)
        except Exception:
            pass

    async def delete_pattern(self, pattern: str) -> None:
        client = await self._get_client()
        if client is None:
            return
        try:
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
        except Exception:
            pass

    async def exists(self, key: str) -> bool:
        client = await self._get_client()
        if client is None:
            return False
        try:
            return await client.exists(key) > 0
        except Exception:
            return False

cache_service = CacheService()