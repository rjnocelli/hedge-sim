from pydantic import BaseModel, Field, validator
from typing import Optional
from .enums import AssetClass, Side, OrderType, OrderStatus
from .config import settings

class OrderIn(BaseModel):
    asset_class: AssetClass
    symbol: str = Field(...)
    side: Side
    quantity: float = Field(..., gt=0)
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = Field(None, gt=0)
    client_id: Optional[str] = None

    @validator("symbol")
    def validate_symbol(cls, v, values):
        ac = values.get("asset_class")
        if ac == AssetClass.CRYPTO and v not in settings.symbols_crypto:
            raise ValueError(f"Unsupported crypto symbol: {v}")
        if ac == AssetClass.EQUITY and v not in settings.symbols_equity:
            raise ValueError(f"Unsupported equity symbol: {v}")
        if ac == AssetClass.INDEX and v not in settings.symbols_index:
            raise ValueError(f"Unsupported index symbol: {v}")
        return v

    @validator("limit_price")
    def limit_price_required_for_limit(cls, v, values):
        if values.get("order_type") == OrderType.LIMIT and v is None:
            raise ValueError("limit_price is required for LIMIT orders")
        return v

class OrderOut(BaseModel):
    id: int 
    asset_class: AssetClass
    symbol: str
    side: Side
    quantity: float
    order_type: OrderType
    limit_price: Optional[float]
    status: OrderStatus
    created_ts: str

class PositionOut(BaseModel):
    symbol: str
    spot_qty: float
    perp_qty: float
    usd_delta: float
        
