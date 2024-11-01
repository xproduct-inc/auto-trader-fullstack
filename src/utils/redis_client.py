from redis.asyncio import Redis
from src.core.config import get_settings
from typing import Optional, Any
import json

settings = get_settings()

class RedisClient:
    def __init__(self):
        self.redis: Optional[Redis] = None

    async def connect(self) -> None:
        if not self.redis:
            self.redis = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )

    async def disconnect(self) -> None:
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def set_data(self, key: str, value: Any, expire: int = 15) -> None:
        """Store data with 15-second default expiry"""
        await self.redis.set(key, json.dumps(value), ex=expire)

    async def get_data(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def publish(self, channel: str, message: Any) -> None:
        await self.redis.publish(channel, json.dumps(message)) 