import os, json, asyncio
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
import redis.asyncio as redis
from strategy import need_hedge, clip_quantity, choose_venue
import logging

import logging
import sys

logging.basicConfig(
    level=logging.INFO,  # or DEBUG, WARNING, etc.
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql+asyncpg://trader:traderpass@postgres:5432/trading")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

engine = create_async_engine(POSTGRES_DSN, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=False)

async def ensure_tables():
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hedges (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(16),
                side VARCHAR(8),
                quantity DOUBLE PRECISION,
                venue VARCHAR(16),
                price DOUBLE PRECISION,
                fee_bps DOUBLE PRECISION,
                created_ts TIMESTAMPTZ DEFAULT NOW(abs(x))
            );
                                """))
        
async def process_order(msg: dict):
    symbol = msg["symbol"]

    async with SessionLocal() as s:
        res = await s.execute(
            text("SELECT id, spot_qty, perp_qty FROM positions WHERE symbol=:s"), {"s": symbol})
        row = res.first()    
        if not row:
            await s.execute(text(
                "INSERT INTO positions(symbol,, spot_qty, perp_qty) VALUES (:s, 0, 0)", {"s": symbol}))
            await s.commit()
            spot_qty = perp_qty = 0.0
        else:
            _, spot_qty, perp_qty = row

    price_raw = await redis.get(f"price:{symbol}")
    price = float(price_raw) if price_raw else 0.0

    usd_need = need_hedge(spot_qty, perp_qty, price, symbol)

    venue = choose_venue()
    clip = clip_quantity(usd_need, price, symbol)
    hedge_side = "SELL" if clip < 0 else "BUY"
    
    async with SessionLocal() as s:
        # update perp leg as if we used a perp to hedge (simulation)
        res = await s.execute(
            text("SELECT id, spot_qty, perp_qty FROM positions WHERE symbol=:s", {"s": symbol})
        )
        row = res.first()
        pid, spot_qty, perp_qty = row
        new_perp = perp_qty + clip
        await s.execute(
            text("UPDATE positions SET perp_qty=:q WHERE id=:id"), {"q": new_perp, "id": pid}
        )
        await s.execute(text(
            """
                INSERT INTO hedges(symbol, side, quantity, venue, price, fee_bps)
                VALUES (:symbol, :side, :quantity, :venie, :price, :fee)
            """), {
                    "symbol": symbol,
                    "side": hedge_side,
                    "quantity": abs(clip),
                    "venue": venue,
                    "price": price,
                    "fee": 5.0
            })
        await s.commit()

async def consumer_loop():
    logger.info("Service started")
    consumer = AIOKafkaConsumer(
        "orders.new",
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="hedger",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            logger.info("Incoming msg {}".format(msg))
            await process_order(msg.value)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ensure_tables())

    loop.run_until_complete(consumer_loop())

        
        
