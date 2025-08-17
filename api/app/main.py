from fastapi import FastAPI
from db import init_db
from routes  import router
from kafka import kafka
app = FastAPI(title="HedgeSim - Order API", version="1.0.0")
app.include_router(router)

@app.on_event("startup")
async def on_startup():
    await init_db()
    await kafka.start()

@app.on_event("shutdown")
async def on_sutdown():
    kafka.stop()
