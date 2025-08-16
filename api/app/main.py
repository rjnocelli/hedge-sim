from fastapi import FastAPI
from db import init_db

app = FastAPI(title="HedgeSim - Order API", version="1.0.0")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.on_event("shutdown")
async def on_sutdown():
    return
