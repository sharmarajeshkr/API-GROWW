import requests
from bs4 import BeautifulSoup
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def test_sector(url):
    print(f"Fetching {url}...")
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if script_tag:
            data = json.loads(script_tag.string)
            print("PageProps keys:", data.get('props', {}).get('pageProps', {}).keys())
            page_props = data.get('props', {}).get('pageProps', {})
            # Look for stocks list
            if 'stocks' in page_props:
                print(f"Found {len(page_props['stocks'])} stocks")
                if len(page_props['stocks']) > 0:
                    print("Sample:", page_props['stocks'][0].get('searchId'), page_props['stocks'][0].get('companyName'))
            elif 'content' in page_props:
                print(f"Found {len(page_props['content'])} items")
            else:
                print("No stocks list found in pageProps")
        else:
            print("No __NEXT_DATA__ found.")
    else:
        print("Failed:", r.status_code)

if __name__ == "__main__":
    test_sector("https://groww.in/sectors/banking")
    test_sector("https://groww.in/mutual-funds/category/equity-mutual-funds")
