import os
import requests
from clickhouse_driver import Client

COINS = ["bitcoin", "ethereum"]


def fetch_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": ",".join(COINS)}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def write_clickhouse(data):
    client = Client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 9000)),
        user=os.getenv("CLICKHOUSE_USER", "admin"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "admin"),
    )
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS market (
            id String,
            symbol String,
            price Float64,
            ts DateTime DEFAULT now()
        ) ENGINE = MergeTree ORDER BY ts
        """
    )
    rows = [(d["id"], d["symbol"], d["current_price"]) for d in data]
    client.execute("INSERT INTO market (id, symbol, price) VALUES", rows)


def main():
    data = fetch_prices()
    write_clickhouse(data)


if __name__ == "__main__":
    main()
