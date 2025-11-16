#!usrbinenv python3

Hourly Market Scanner
Fetches active hourly markets and saves top 5 IDs.


import json
from limitless_auth import get_session

API_URL = httpsapi.limitless.exchange

def get_active_markets(session, limit=25, page=1)
    url = f{API_URL}marketsactive
    params = {limit str(limit), page str(page)}
    r = session.get(url, params=params, timeout=30)
    payload = r.json()
    return payload.get(markets, []) or payload.get(data, [])

def scan_hourly()
    session = get_session()
    all_markets = get_active_markets(session, limit=25, page=1)
    hourly_markets = [m for m in all_markets if Hourly in m.get(categories, [])]
    top5 = hourly_markets[5]
    ids = [m[id] for m in top5]

    print(f[LLMM] Hourly markets IDs {ids})

    # Save to file for live streaming script
    with open(hourly_ids.json, w) as f
        json.dump(ids, f)

if __name__ == __main__
    scan_hourly()
