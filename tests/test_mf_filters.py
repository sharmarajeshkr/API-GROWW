import requests

def test_sub_cat():
    url = "https://groww.in/v1/api/search/v1/derived/scheme"
    params = {
        "available_for_investment": "true",
        "sub_category": "Large Cap",
        "page": "0",
        "size": "50"
    }
    
    print(f"GET {url}")
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params=params)
    print("API Status:", r.status_code)
    
    if r.status_code == 200:
        resp = r.json()
        print(f"Total Large Cap MFs retrieved: {resp.get('total_results')} / {len(resp.get('content', []))}")
    else:
        print(r.text)

if __name__ == "__main__":
    test_sub_cat()
