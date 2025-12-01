import redis.asyncio as redis

from app.core.config import settings

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            ssl_cert_reqs=None,
        )
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def is_blacklisted(token: str) -> bool:
    client = await get_redis()
    result = await client.exists(f"blacklist:{token}")
    return result > 0
