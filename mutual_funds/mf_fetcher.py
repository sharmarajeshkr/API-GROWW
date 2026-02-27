import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import sys
import os

# Appending root directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger("mf_fetcher")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_sector_mfs(sector_category="Equity"):
    """Fetches mutual fund names and details for a given category/sector from Groww frontend."""
    # categories: Equity, Debt, Hybrid
    # We encode ["Equity"] to %5B%22Equity%22%5D
    encoded_category = urllib.parse.quote(json.dumps([sector_category]))
    url = f"https://groww.in/mutual-funds/filter?category={encoded_category}"
    logger.debug(f"Fetching {url}...")
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        logger.error(f"Failed to fetch page: {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if not script_tag:
         logger.warning("No __NEXT_DATA__ found on mutual funds page.")
         return []

    data = json.loads(script_tag.string)
    page_props = data.get('props', {}).get('pageProps', {})
    mf_screener_data = page_props.get('mfScreenerData', {})
    
    if isinstance(mf_screener_data, dict):
        if 'content' in mf_screener_data:
            records = mf_screener_data['content']
            logger.info(f"Successfully found {len(records)} MFs for category {sector_category}")
            return records
        else:
             logger.debug(f"mfScreenerData keys: {mf_screener_data.keys()}")
             for k,v in mf_screener_data.items():
                 if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                     return v
    return []

if __name__ == "__main__":
    equity_mfs = get_sector_mfs("Equity")
    print("\nSAMPLE EQUITY MUTUAL FUNDS:")
    for mf in equity_mfs[:3]:
        name = mf.get('search_id') or mf.get('schemeName') or mf.get('title')
        print(f"- {name} | 3Y Return: {mf.get('return3y')}%")
