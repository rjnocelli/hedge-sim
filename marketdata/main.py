import os, asyncio, json, random, time
from aiokafka import AIOKafkaProducer
import redis.asyncio as redis

from prometheus_client import Counter, Gauge, make_asgi_app
import uvicorn
from fastapi import FastAPI

try:
    import ccxt
except Exception:
    ccxt = None

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
USE_CCXT = os.getenv("USE_CCXT", "true").lower() == "true"
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SEC", "10"))
TICK_INTERVAL_MS = int(os.getenv("TICK_INTERVAL_MS", "500"))
SYMBOLS = ["BTCUSDT", "ETHUSDT", "NVDA", "SPX"]

redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
prices = {s: 0.0 for s in SYMBOLS}

producer: AIOKafkaProducer | None = None

price_ticks = Counter("md_ticks_total", "Market data ticks", ["symbol", "source"]) 
price_gauge = Gauge("md_price", "Latest price", ["symbol"])
metrics_app = make_asgi_app()
app = FastAPI()
app.mount("/metrics", metrics_app)

async def publish(symbol: str, price: float, source: str):
    await redis.set(f"price:{symbol}", price)
    price_gauge.labels(symbol).set(price)
    price_ticks.labels(symbol, source).inc()    
    payload = {
        "symbol": symbol, "price": price, "ts": time.time(), "source": source}
    assert producer is not None
    await producer.send_and_wait("marketdata.updates", payload)

async def poll_real_prices():
    if not USE_CCXT or ccxt is None:
        return

    binance = ccxt.binance()
    while True:
        for sym in ["BTCUSDT", "ETHUSDR"]:
            try:
                t = await asyncio.to_thread(binance.fetch_ticker, sym.replace("USDT", "/USDT"))
                prices[sym] = t["last"]
                await publish(sym, prices[sym], "binance")
            except Exception:
                pass
        await asyncio.sleep(POLL_INTERVAL)

async def synthetic_ticks():
    prices.setdefault("BTCUSDT", prices.get("BTCUSDT", 67000.0) or 67000.0)
    prices.setdefault("ETHUSDT", prices.get("ETHUSDT", 3500.0) or 3500.0)
    prices.setdefault("NVDA", prices.get("NVDA", 120.0) or 120.0)   # post-split style price
    prices.setdefault("SPX", prices.get("SPX", 5500.0) or 5500.0)
    while True:
        for s in SYMBOLS:
            mu = 0.0
            sigma = {
                "BTCUSDT": 2.0,
                "ETHUSDT": 1.0,
                "NVDA": 0.5,
                "SPX": 0.3,
            }[s]
            prices[s] = max(0.01, prices.get(s, 100.0) + random.gauss(mu, sigma))
            await publish(s, prices[s], "synthetic")
        await asyncio.sleep(TICK_INTERVAL_MS / 1000.0)

async def main():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        client_id="hedgesim-marketdata",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()
    import threading
    def run_metrics():
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="warning")
    threading.Thread(target=run_metrics, daemon=True).start()
    await asyncio.gather(
        synthetic_ticks(),
        poll_real_prices()
    )

if __name__ == "__main__":
    asyncio.run(main())
