from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import asyncio
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API WORKING"}

@app.get("/stock/{symbol}")
def get_stock(symbol: str):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d", interval="1m")

    if hist.empty:
        return {"error": "No data"}

    return {
        "symbol": symbol.upper(),
        "price": float(hist["Close"].iloc[-1]),
        "open": float(hist["Open"].iloc[-1]),
        "high": float(hist["High"].iloc[-1]),
        "low": float(hist["Low"].iloc[-1]),
        "volume": int(hist["Volume"].iloc[-1])
    }

@app.websocket("/ws/{symbol}")
async def websocket_price(websocket: WebSocket, symbol: str):
    await websocket.accept()
    while True:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                await websocket.send_json({
                    "symbol": symbol.upper(),
                    "price": price
                })
            await asyncio.sleep(5)
        except:
            await websocket.send_json({"error": "data error"})
            await asyncio.sleep(5)
