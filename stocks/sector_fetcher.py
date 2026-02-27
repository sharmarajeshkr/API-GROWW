import requests
from bs4 import BeautifulSoup
import json
import sys
import os

# Appending root directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger("sector_fetcher")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_sector_stocks(sector_name="Banking"):
    """Fetches stock names and details for a given sector from Groww frontend."""
    url = f"https://groww.in/stocks/filter?sectors={sector_name}"
    logger.debug(f"Fetching {url}...")
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        logger.error(f"Failed to fetch page: {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if not script_tag:
         logger.warning("No __NEXT_DATA__ found on stock sector page.")
         return []

    data = json.loads(script_tag.string)
    page_props = data.get('props', {}).get('pageProps', {})
    screener_data = page_props.get('screenerData', {})
    
    if isinstance(screener_data, dict):
        if 'records' in screener_data:
            records = screener_data['records']
            logger.info(f"Successfully found {len(records)} stocks for sector {sector_name}")
            return records
        elif 'content' in screener_data:
            records = screener_data['content']
            logger.info(f"Successfully found {len(records)} stocks in 'content' for sector {sector_name}")
            return records
        else:
             logger.debug(f"screenerData keys: {screener_data.keys()}")
             for k,v in screener_data.items():
                 if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                     return v
    return []

if __name__ == "__main__":
    banking_stocks = get_sector_stocks("Banking")
    print("\nSAMPLE BANKING STOCKS:")
    for stock in banking_stocks[:3]:
        print(f"- {stock.get('companyName')} (Symbol: {stock.get('searchId')}) | Close: {stock.get('closePrice')}")
