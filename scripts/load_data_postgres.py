import os
import requests
import psycopg2


COINS = ["bitcoin", "ethereum"]


def fetch_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": ",".join(COINS)}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def write_postgres(data):
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        dbname=os.getenv("POSTGRES_DB", "app"),
    )
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS market(
            id text,
            symbol text,
            price double precision,
            ts timestamp DEFAULT now()
        );
        """
    )
    for d in data:
        cur.execute(
            "INSERT INTO market (id, symbol, price) VALUES (%s, %s, %s)",
            (d["id"], d["symbol"], d["current_price"]),
        )
    conn.commit()
    cur.close()
    conn.close()


def main():
    data = fetch_prices()
    write_postgres(data)


if __name__ == "__main__":
    main()
