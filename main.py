from fastapi import FastAPI
import ccxt
from dotenv import load_dotenv
import os
from helpers import get_binance_deposit_address, withdraw_to_network

# Load environment variables from .env file
load_dotenv()

exchange = ccxt.binanceus(
    {
        "apiKey": os.getenv("BINANCE_API_KEY"),
        "secret": os.getenv("BINANCE_API_SECRET"),
    }
)

app = FastAPI()


@app.get("/deposit-address")
async def deposit_address(token: str, network: str):
    address = get_binance_deposit_address(exchange, network, token)
    return {"address": address}


@app.get("/withdraw")
async def withdraw(token: str, amount: float, address: str, network: str):
    withdrawal = withdraw_to_network(exchange, token, amount, address, network)
    return {"withdrawal": withdrawal}


@app.get("/balance")
async def balance():
    balance = exchange.fetch_balance()
    return {"balance": balance}


@app.get("/currencies")
async def currencies():
    currencies = exchange.fetch_currencies()
    return {"currencies": currencies}
