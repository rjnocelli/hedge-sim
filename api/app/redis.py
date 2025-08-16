from redis.asyncio import Redis
from config import settings

redis = Redis.from_url(settings.redis_url, decode_responses=True)

async def set_price(symbol: str, price: float):
    await redis.set(f"price:{symbol}", float)

async def get_price(symbol: str) -> float | None:
    val = await redis.get(f"price:{symbol}")
    return float(val) if val is not None else None
