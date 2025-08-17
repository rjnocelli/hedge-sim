import asyncio
import random
import httpx
from datetime import datetime
from config import settings
from enums import AssetClass, Side, OrderType

API_URL = "http://api:8000/orders"

SYMBOLS = {
    AssetClass.CRYPTO: settings.symbols_crypto,
    AssetClass.EQUITY: settings.symbols_equity,
    AssetClass.INDEX: settings.symbols_index,
}

SIDES = [Side.BUY, Side.SELL]

async def create_random_order():
    asset_class = random.choice(list(SYMBOLS.keys()))
    symbol = random.choice(SYMBOLS[asset_class])
    side = random.choice(SIDES)
    quantity = round(random.uniform(0.1, 5.0), 2)
    
    order_type = OrderType.MARKET
    limit_price = None
 
    if random.random() < 0.3:
        order_type = OrderType.LIMIT
        limit_price = round(random.uniform(100, 500), 2)

    payload = {
        "asset_class": asset_class.value,
        "symbol": symbol,
        "side": side.value,
        "quantity": quantity,
        "order_type": order_type.value,
        "limit_price": limit_price,
        "client_id": f"sim-{datetime.utcnow().timestamp()}"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(API_URL, json=payload)
        if resp.status_code == 200 or resp.status_code == 201:
            print(f"Order sent: {payload}")
        else:
            print(f"Failed to send order: {resp.text}")

async def run_generator(interval_sec: int = 1):
    while True:
        try:
            await create_random_order()
        except httpx.ConnectError:
            # NOTE: make sure api is running already
            await asyncio.sleep(10)
        
        await asyncio.sleep(interval_sec)

if __name__ == "__main__":
    asyncio.run(run_generator())
