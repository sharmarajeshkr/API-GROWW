import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    # Let's test if we can get a list of stocks with sectors
    url_stocks = "https://groww.in/v1/api/stocks_data/explore/v2/filters"
    payload = {
        "listFilters": {"INDUSTRY": [], "MARKET_CAP": [], "INDEX": []},
        "sortBy": "MARKET_CAP",
        "sortType": "DESC",
        "page": 0,
        "size": 10
    }
    r = requests.post(url_stocks, headers=headers, json=payload)
    if r.status_code == 200:
        print("Stocks API Response Keys:")
        print(r.json().keys())
        if "records" in r.json() and len(r.json()["records"]) > 0:
            print("First Stock Record Keys:")
            print(r.json()["records"][0].keys())
    else:
        print("Stocks API Failed:", r.status_code, r.text[:200])
        
    # Testing another endpoint commonly used to get stock lists
    r2 = requests.get("https://groww.in/v1/api/search/v1/derived/scheme", headers=headers)
    print("\nMutual Funds Scheme Search Status:", r2.status_code)
    
except Exception as e:
    print("Error:", e)
