import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app, exchange

client = TestClient(app)


@patch("helpers.get_binance_deposit_address")
def test_deposit_address_success(mock_get_deposit_address):
    mock_get_deposit_address.return_value = "sample_address"
    response = client.get("/deposit-address", params={"token": "BTC", "network": "BTC"})

    assert response.status_code == 200, "Expected a 200 OK status code"
    assert response.json() == {
        "address": "sample_address"
    }, "Expected the response to contain the sample address"

    mock_get_deposit_address.assert_called_with(exchange, "BTC", "BTC")


@patch("helpers.get_binance_deposit_address")
def test_deposit_address_failure(mock_get_deposit_address):
    mock_get_deposit_address.return_value = None

    response = client.get("/deposit-address", params={"token": "BTC", "network": "BTC"})

    assert response.status_code == 200, "Expected a 200 OK status code even for failure"
    assert response.json() == {
        "address": None
    }, "Expected the response to contain None as the address"


@patch("helpers.withdraw_to_network")
def test_withdraw_success(mock_withdraw):
    mock_withdraw.return_value = {"id": "withdrawal_id"}

    response = client.get(
        "/withdraw",
        params={
            "token": "BTC",
            "amount": 0.1,
            "address": "sample_address",
            "network": "BTC",
        },
    )

    assert response.status_code == 200, "Expected a 200 OK status code"
    assert response.json() == {
        "withdrawal": {"id": "withdrawal_id"}
    }, "Expected the response to contain the withdrawal ID"

    mock_withdraw.assert_called_with(exchange, "BTC", 0.1, "sample_address", "BTC")


@patch("helpers.withdraw_to_network")
def test_withdraw_failure(mock_withdraw):
    mock_withdraw.return_value = None

    response = client.get(
        "/withdraw",
        params={
            "token": "BTC",
            "amount": 0.1,
            "address": "sample_address",
            "network": "BTC",
        },
    )

    assert response.status_code == 200, "Expected a 200 OK status code even for failure"
    assert response.json() == {
        "withdrawal": None
    }, "Expected the response to contain None as the withdrawal"


@patch.object(exchange, "fetch_balance")
def test_balance_success(mock_fetch_balance):
    mock_fetch_balance.return_value = {"BTC": {"free": 1.0, "used": 0.0, "total": 1.0}}

    response = client.get("/balance", params={"token": "BTC"})

    assert response.status_code == 200, "Expected a 200 OK status code"
    assert response.json() == {
        "balance": {"BTC": {"free": 1.0, "used": 0.0, "total": 1.0}}
    }, "Expected the response to contain the sample balance"

    mock_fetch_balance.assert_called_with(token="BTC")


@patch.object(exchange, "fetch_balance")
def test_balance_failure(mock_fetch_balance):
    mock_fetch_balance.side_effect = Exception("Error fetching balance")

    response = client.get("/balance", params={"token": "BTC"})

    assert (
        response.status_code == 500
    ), "Expected a 500 Internal Server Error status code for balance fetch failure"


@patch.object(exchange, "fetch_currencies")
def test_currencies_success(mock_fetch_currencies):
    mock_fetch_currencies.return_value = {"BTC": {}, "ETH": {}}

    response = client.get("/currencies")

    assert response.status_code == 200, "Expected a 200 OK status code"
    assert response.json() == {
        "currencies": {"BTC": {}, "ETH": {}}
    }, "Expected the response to contain the sample currencies"

    mock_fetch_currencies.assert_called_once()


@patch.object(exchange, "fetch_currencies")
def test_currencies_failure(mock_fetch_currencies):
    mock_fetch_currencies.side_effect = Exception("Error fetching currencies")

    response = client.get("/currencies")

    assert (
        response.status_code == 500
    ), "Expected a 500 Internal Server Error status code for currencies fetch failure"
