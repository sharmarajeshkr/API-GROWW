import requests
import json
from bs4 import BeautifulSoup

def fetch_banking_stocks():
    # 1. Get the mapping of Sector -> Industry IDs
    url_filter = "https://groww.in/stocks/filter"
    r1 = requests.get(url_filter, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r1.text, 'html.parser')
    tag = soup.find('script', id='__NEXT_DATA__')
    data = json.loads(tag.string)
    
    industries = data.get('props', {}).get('pageProps', {}).get('ssrDefaultFilters', {}).get('filterData', {}).get('INDUSTRY', [])
    
    banking_ids = []
    for ind in industries:
        if ind.get('sector') == 'Banking':
            banking_ids = list(ind.get('industries', {}).keys())
            break
            
    print(f"Banking Sector mapped to Industry IDs: {banking_ids}")
    
    if not banking_ids:
        print("Banking sector not found!")
        return
        
    # 2. Query the internal API
    url_api = "https://groww.in/v1/api/stocks_data/v1/all_stocks"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    payload = {
      "listFilters": {
        "INDUSTRY": banking_ids,
        "INDEX": []
      },
      "objFilters": {
        "CLOSE_PRICE": {"max": 100000, "min": 0},
        "MARKET_CAP": {"min": 0, "max": 3000000000000000}
      },
      "page": "0",
      "size": "100",
      "sortBy": "NA",
      "sortType": "ASC"
    }
    
    r2 = requests.post(url_api, headers=headers, json=payload)
    print("API Status:", r2.status_code)
    
    if r2.status_code == 200:
        resp = r2.json()
        print(f"Total Records returned by API: {resp.get('totalRecords')}")
        records = resp.get('records', [])
        print(f"Fetched {len(records)} items in size=100 window.")
        if records:
            for s in records[:5]:
                print(f" - {s.get('companyName')} (ID: {s.get('searchId')})")
    else:
        print(r2.text)

if __name__ == "__main__":
    fetch_banking_stocks()
