import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://groww.in",
    "Referer": "https://groww.in/"
}

def test_mf_api():
    try:
        # Search mutual funds by sector/category
        url = "https://groww.in/v1/api/search/v1/derived/scheme"
        payload = {
            "filters": {"category": ["Equity"]},
            "size": 15
        }
        r = requests.post(url, headers=headers, json=payload)
        print("MF API Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            print("Categories found in MF response (keys):", data.keys())
            if "content" in data and len(data["content"]) > 0:
                print("First MF item keys:", data["content"][0].keys())
                print("First MF item name:", data["content"][0].get("search_id"))
        else:
            print("Error text:", r.text)
    except Exception as e:
        print("Error:", e)

def test_stocks_api():
    try:
        url = "https://groww.in/v1/api/stocks_data/v1/all_stocks"
        # Try POST instead of GET since 405 means Method Not Allowed
        payload = {
            "page": 0,
            "size": 10,
            "sortType": "ASC",
            "sortBy": "NAME"
        }
        r = requests.post(url, headers=headers, json=payload)
        print("Stocks API POST Status:", r.status_code)
        if r.status_code == 200:
            print("Stocks API keys:", r.json().keys())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_mf_api()
    test_stocks_api()
