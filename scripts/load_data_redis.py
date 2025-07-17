import os
import requests
import redis

COINS = ["bitcoin", "ethereum"]


def fetch_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": ",".join(COINS)}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def write_redis(data):
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )
    for d in data:
        r.hset(
            f"coin:{d['id']}",
            mapping={"symbol": d["symbol"], "price": d["current_price"]},
        )

def main():
    data = fetch_prices()
    write_redis(data)

if __name__ == "__main__":
    main()
