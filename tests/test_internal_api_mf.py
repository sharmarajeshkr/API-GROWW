import requests

def fetch_mutual_funds():
    url = "https://groww.in/v1/api/search/v1/derived/scheme"
    params = {
        "available_for_investment": "true",
        "category": "Equity",
        "page": "0",
        "size": "500"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    print(f"GET {url}")
    r = requests.get(url, headers=headers, params=params)
    print("API Status:", r.status_code)
    
    if r.status_code == 200:
        resp = r.json()
        content = resp.get('content', [])
        print(f"Total Mutual Funds retrieved for Equity: {len(content)}")
        if content:
             for mf in content[:5]:
                 print(f" - {mf.get('scheme_name')} (ID: {mf.get('search_id')})")
    else:
        print(r.text)

if __name__ == "__main__":
    fetch_mutual_funds()
