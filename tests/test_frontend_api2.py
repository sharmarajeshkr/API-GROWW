import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    # Testing all_stocks
    r1 = requests.get("https://groww.in/v1/api/stocks_data/v1/all_stocks", headers=headers)
    print("all_stocks Status:", r1.status_code)
    if r1.status_code == 200:
        data = r1.json()
        print("all_stocks keys:", data.keys() if isinstance(data, dict) else len(data))
    
    # Testing scheme search for sector
    r2 = requests.post("https://groww.in/v1/api/search/v1/derived/scheme", headers=headers, json={"filters": {"category": ["Equity"]}, "size": 10})
    print("\nMutual Funds Status:", r2.status_code)
    
except Exception as e:
    print("Error:", e)
