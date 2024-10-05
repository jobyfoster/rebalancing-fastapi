def get_binance_deposit_address(exchange, network, token):
    try:
        address_info = exchange.fetch_deposit_address(
            code=token, params={"network": network}
        )
        return address_info["address"]
    except Exception as e:
        print(f"Error fetching deposit address: {str(e)}")
        return None


def withdraw_to_network(exchange, token, amount, address, network):
    try:
        withdrawal = exchange.withdraw(
            code=token,
            amount=amount,
            address=address,
            params={"network": network},
        )
        return withdrawal
    except Exception as e:
        print(f"Error withdrawing to {network}: {str(e)}")
        return None
