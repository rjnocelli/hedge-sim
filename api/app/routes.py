import time
from fastapi import APIRouter, Dependes, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from schemas import OrderIn, OrderOut
from models import Order, Position
from db import get_session
from kafka import kafka
from enums import OrderStatus, OrderType, Side
from redis import get_price

router =APIRouter()

@router.post("/orders", response_model=OrderOut())
async def create_order(payload: OrderIn, session: AsyncSession = Dependes(get_session)):
    if payload.order_type == OrderType.LIMIT.value:
        ref = await get_price(payload.symbol)
        if ref is not None and payload.limit_price is not None:
            if abs(payload.limit_price - ref) / ref > 0.20:
                raise HTTPException(status_code=400, detail="limit_price deviates too much from reference")
    order = Order(
        asset_class=payload.asset_class.value,
        symbol=payload.symbol,
        side=payload.side.value,
        quantity=payload.quantity,
        order_type=payload.order_type.value,
        limit_price=payload.limit_price,
        status=OrderStatus.ACCEPTED.value,
        client_id=payload.client_id,
    )
    session.add(order)
    await session.flush()
    res = await session.execute(
        select(Position).where(Position.symbol == payload.symbol)
    )
    pos = res.scalar_one()
    delta = payload.quantity if payload.side == Side.BUY else -payload.quantity
    new_spot = (pos.spot_qty or 0.0) + delta
    await session.execute(update(Position).where(
                              Position.id == pos.id).values(
                              spot_qty=new_spot))
    await session.commit()
    await kafka.publish_order({
            "order_id": order.id,
            "asset_class": payload.asset_class.value,
            "symbol": payload.symbol,
            "side": payload.side.value,
            "quantity": payload.quantity,
            "order_type": payload.order_type.value,
            "limit_price": payload.limit_price,
            "ts": time.time(),
        })
    return OrderOut(
        id=order.id,
        asset_class=payload.asset_class,
        symbol=payload.symbol,
        side=payload.side,
        quantity=payload.quantity,
        order_type=payload.order_type,
        limit_price=payload.limit_price,
        status=OrderStatus.ACCEPTED,
        created_ts=str(order.created_ts)
    )
    
