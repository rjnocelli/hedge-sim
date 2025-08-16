import os
from typing import Dict

HEDGE_BAND = {
    "BTCUSDT": float(os.getenv("HEDGE_BAND_USD_BTC", 50000)),
    "ETHUSDT": float(os.getenv("HEDGE_BAND_USD_ETH", 20000)),
    "NVDA": float(os.getenv("HEDGE_BAND_USD_NVDA", 10000)),
    "SPX": float(os.getenv("HEDGE_BAND_USD_SPX", 20000)),
}

CLIP_USD = {
    "BTCUSDT": float(os.getenv("CLIP_USD_BTC", 25000)),
    "ETHUSDT": float(os.getenv("CLIP_USD_ETH", 10000)),
    "NVDA": float(os.getenv("CLIP_USD_NVDA", 5000)),
    "SPX": float(os.getenv("CLIP_USD_SPX", 10000)),
}

VENUE_FEES_BPS = {"binance": 4.0, "okx": 5.0, "kraken": 6.0}

def need_hedge(spot_qty: float, perp_qty: float, price: float, symbol: str) -> float:
    """Return USD exposure; 0 if within band."""
    usd = (spot_qty + perp_qty) * price
    band = HEDGE_BAND.get(symbol, 10000.0)
    return 0.0 if abs(usd) <= band else usd

def clip_quantity(usd_needed: float, price: float, symbol: str) -> float:
    sign = -1 if usd_needed > 0 else 1 # long exposure -> sell (negative qty)
    notional = min(abs(usd_needed), CLIP_USD.get(symbol, 5000.0))
    return sign * (notional / max(price, 1e-9))

def choose_venue() -> str:
    # Simplified logic: choose min fee venue
    return min(VENUE_FEES_BPS, key=VENUE_FEES_BPS.get)
    
