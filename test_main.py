import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, exchange

client = TestClient(app)


@patch("helpers.get_binance_deposit_address")
def test_deposit_address(mock_get_deposit_address):
    # Test success scenario
    mock_get_deposit_address.return_value = {
        "address": "1HPn8Rx2y6nNSfagQBKy27GB99Vbzg89wv"
    }
    response = client.get("/deposit-address?token=BTC&network=BTC")
    assert response.status_code == 200
    assert "address" in response.json()
    assert isinstance(response.json()["address"], str)
    assert len(response.json()["address"]) > 0

    # Test failure scenario
    mock_get_deposit_address.return_value = None
    response = client.get("/deposit-address?token=BTC&network=BTC")
    assert response.status_code == 200
    assert response.json() == {"address": None}


@patch("helpers.withdraw_to_network")
@patch("toml.load")
def test_withdraw(mock_toml_load, mock_withdraw):
    # Mock the toml.load function to return a predefined accounts dictionary
    mock_toml_load.return_value = {
        "accounts": [{"name": "test-account", "address": "test_address"}]
    }

    # Test success scenario
    mock_withdraw.return_value = {"id": "7213fea8e94b4a5593d507237e5a555b"}
    response = client.get(
        "/withdraw?token=BTC&amount=0.1&account_name=test-account&network=BTC"
    )
    assert response.status_code == 200
    assert "withdrawal" in response.json()
    assert "id" in response.json()["withdrawal"]
    assert isinstance(response.json()["withdrawal"]["id"], str)
    assert len(response.json()["withdrawal"]["id"]) == 32

    # Test account not found scenario
    response = client.get(
        "/withdraw?token=BTC&amount=0.1&account_name=non-existent&network=BTC"
    )
    assert response.status_code == 200
    assert response.json() == {"error": "Account 'non-existent' not found"}

    # Test failure scenario
    mock_withdraw.return_value = None
    response = client.get(
        "/withdraw?token=BTC&amount=0.1&account_name=test-account&network=BTC"
    )
    assert response.status_code == 200
    assert response.json() == {"withdrawal": None}


@patch.object(exchange, "fetch_balance")
def test_balance(mock_fetch_balance):
    # Test success scenario
    mock_balance = {
        "balance": {
            "info": {},
            "timestamp": 1499280391811,
            "datetime": "2017-07-05T18:47:14.692Z",
            "free": {"BTC": 321.00, "USD": 123.00},
            "used": {"BTC": 234.00, "USD": 456.00},
            "total": {"BTC": 555.00, "USD": 579.00},
            "debt": {},
        }
    }
    mock_fetch_balance.return_value = mock_balance
    response = client.get("/balance")
    assert response.status_code == 200
    assert "balance" in response.json()
    balance = response.json()["balance"]
    assert isinstance(balance, dict)
    assert "info" in balance
    assert "timestamp" in balance
    assert isinstance(balance["timestamp"], int)
    assert "datetime" in balance
    assert isinstance(balance["datetime"], str)
    assert "free" in balance
    assert isinstance(balance["free"], dict)
    assert "used" in balance
    assert isinstance(balance["used"], dict)
    assert "total" in balance
    assert isinstance(balance["total"], dict)
    assert "debt" in balance
    assert isinstance(balance["debt"], dict)

    # Test failure scenario
    mock_fetch_balance.side_effect = Exception("Test error")
    response = client.get("/balance")
    assert response.status_code == 200
    assert response.json() == {"balance": None}


@patch.object(exchange, "fetch_currencies")
def test_currencies(mock_fetch_currencies):
    # Test success scenario
    mock_currencies = [
        {
            "coin": "BTC",
            "name": "Bitcoin",
            "networkList": [
                {
                    "network": "BTC",
                    "withdrawFee": "0.00050000",
                },
                {
                    "network": "BNB",
                    "withdrawFee": "0.00000220",
                },
            ],
        },
        {
            "coin": "ETH",
            "name": "Ethereum",
            "networkList": [
                {
                    "network": "ETH",
                    "withdrawFee": "0.005",
                }
            ],
        },
    ]
    mock_fetch_currencies.return_value = mock_currencies
    response = client.get("/currencies")
    assert response.status_code == 200
    assert "currencies" in response.json()
    currencies = response.json()["currencies"]
    assert isinstance(currencies, list)
    assert len(currencies) > 0
    for currency in currencies:
        assert "coin" in currency
        assert "name" in currency
        assert "networkList" in currency
        assert isinstance(currency["networkList"], list)
        for network in currency["networkList"]:
            assert "network" in network
            assert "withdrawFee" in network

    # Test failure scenario
    mock_fetch_currencies.side_effect = Exception("Test error")
    response = client.get("/currencies")
    assert response.status_code == 200
    assert response.json() == {"currencies": None}
