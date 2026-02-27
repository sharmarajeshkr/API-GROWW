import requests
from bs4 import BeautifulSoup
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def test_url(url):
    print(f"\n--- Fetching {url} ---")
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if script_tag:
            data = json.loads(script_tag.string)
            page_props = data.get('props', {}).get('pageProps', {})
            print("PageProps keys:", page_props.keys())
            
            # Check stocks
            if 'filterData' in page_props:
                records = page_props['filterData'].get('records', [])
                print(f"Found {len(records)} records in filterData")
                if records:
                    print("Sample record:", records[0].get('searchId'), records[0].get('companyName'), records[0].get('industryName'))
                    
            elif 'initialFilters' in page_props:
                print("Found initialFilters in pageProps")
                
            # For mutual funds there might be a different key
            elif 'mfList' in page_props or 'content' in page_props:
                 print("Found mfList or content")
            else:
                 # let's just dump a few keys
                 print("Other keys inside pageProps:")
                 for k, v in page_props.items():
                     if isinstance(v, (dict, list)):
                         print(f"  {k}: length/size {len(v)}")
                     else:
                         print(f"  {k}: {type(v)}")
        else:
            print("No __NEXT_DATA__ found.")
    else:
        print("Failed:", r.status_code)

if __name__ == "__main__":
    test_url("https://groww.in/stocks/filter?sectors=Banking")
    test_url("https://groww.in/mutual-funds/filter?category=%5B%22Equity%22%5D")
