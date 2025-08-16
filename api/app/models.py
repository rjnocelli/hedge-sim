from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, DateTime, func
from enums import OrderStatus

Base =declarative_base()

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_class: Mapped[str] = mapped_column(String(16), nullable=False)
    symbol: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    order_type: Mapped[str] = mapped_column(String(8), nullable=False)
    limit_price: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default=OrderStatus.ACCEPTED.value)
    client_id: Mapped[str] = mapped_column(String(64), nullable=True)
    created_ts: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
class Position(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    spot_qty: Mapped[float] = mapped_column(Float, default=0.0)
    perp_qty: Mapped[float] = mapped_column(Float, default=0.0)
    updated_ts: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
class Hedge(Base):
    __tablename__ = "hedges"    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    side: Mapped[str] = mapped_column(String(8))
    quantity: Mapped[float] = mapped_column(Float)
    venue: Mapped[str] = mapped_column(String(16))
    price: Mapped[float] = mapped_column(Float)
    fee_bps: Mapped[float] = mapped_column(Float)
    created_ts: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
