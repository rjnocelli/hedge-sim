from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from config import settings
from models import Base

engine = create_async_engine(settings.postgres_dsn, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for sym in settings.symbols_crypto + settings.symbols_equity + settings.symbols_index:
            await conn.execute(text("""
                 INSERT INTO positions(symbol, spot_qty, perp_qty)
                 VALUES (:s, 0, 0)
                 ON CONFLICT (symbol) DO NOTHING
                 """), {"s": sym})
 
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
