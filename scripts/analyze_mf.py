import requests
import json
from bs4 import BeautifulSoup

def find_api():
    url = "https://groww.in/mutual-funds/hdfc-top-200-fund"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, 'html.parser')
    tag = soup.find('script', id='__NEXT_DATA__')
    data = json.loads(tag.string)
    
    urls = set()
    def search_tree(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str) and ('http' in v or '/api/' in v or 'data' in v):
                    urls.add(v)
                search_tree(v)
        elif isinstance(d, list):
            for v in d:
                if isinstance(v, str) and ('http' in v or '/api/' in v or 'data' in v):
                    urls.add(v)
                search_tree(v)
                
    search_tree(data)
    for u in sorted(urls):
        print(u[:150])

if __name__ == "__main__":
    find_api()
