from fastapi import FastAPI
import ccxt
from dotenv import load_dotenv
import os
import toml
from helpers import get_binance_deposit_address, withdraw_to_network

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
async def withdraw(token: str, amount: float, account_name: str, network: str):
    with open("accounts.toml", "r") as f:
        accounts = toml.load(f)

    # Find the address for the given account name
    address = None
    for account in accounts.get("accounts", []):
        if account.get("name") == account_name:
            address = account.get("address")
            break

    if not address:
        return {"error": f"Account '{account_name}' not found"}

    balance = exchange.fetch_balance()
    token_balance = balance["free"][token]
    if token_balance is None:
        return {"error": f"Unable to fetch balance for {token}"}

    if token_balance < amount:
        return {"error": f"Insufficient balance for {token}"}

    withdrawal = withdraw_to_network(exchange, token, amount, address, network)
    return {"withdrawal": withdrawal}


@app.get("/balance")
async def balance(token: str = None):
    try:
        balance = exchange.fetch_balance()
        if token:
            if token in balance["free"]:
                return {
                    "balance": {
                        "free": balance["free"][token],
                        "used": balance["used"][token],
                        "total": balance["total"][token],
                    }
                }
            else:
                return {"error": f"Token {token} not found in balance"}
        return {"balance": balance}
    except Exception as e:
        print(f"Error fetching balance: {str(e)}")
        return {"balance": None}


@app.get("/currencies")
async def currencies():
    try:
        currencies = exchange.fetch_currencies()
        return {"currencies": currencies}
    except Exception as e:
        print(f"Error fetching currencies: {str(e)}")
        return {"currencies": None}
