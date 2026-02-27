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

def get_all_sectors():
    """Fetches the comprehensive list of all stock sectors available on Groww."""
    url = "https://groww.in/stocks/filter"
    logger.debug(f"Fetching all sectors from {url}...")
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        logger.error(f"Failed to fetch sectors page: {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if not script_tag:
         logger.warning("No __NEXT_DATA__ found on stock sector page.")
         return []

    try:
        data = json.loads(script_tag.string)
        props = data.get('props', {}).get('pageProps', {})
        industries = props.get('ssrDefaultFilters', {}).get('filterData', {}).get('INDUSTRY', [])
        
        sectors = []
        for ind in industries:
            if 'sector' in ind:
                sectors.append(ind['sector'])
                
        logger.info(f"Successfully dynamically fetched {len(sectors)} stock sectors")
        return sectors
    except Exception as e:
        logger.error(f"Failed to parse sector list: {e}")
        return []

def get_sector_stocks(sector_name="Banking"):
    """Fetches comprehensive stock names and details for a given sector from Groww internal backend API."""
    logger.debug(f"Fetching all stocks for sector {sector_name}...")
    
    # First, get the mapping of Sector -> Industry IDs safely from hydration state
    url_filter = "https://groww.in/stocks/filter"
    r1 = requests.get(url_filter, headers=headers)
    if r1.status_code != 200:
        logger.error(f"Failed to fetch sectors page for mapping: {r1.status_code}")
        return []
        
    soup = BeautifulSoup(r1.text, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    banking_ids = []
    if script_tag:
        try:
            data = json.loads(script_tag.string)
            industries = data.get('props', {}).get('pageProps', {}).get('ssrDefaultFilters', {}).get('filterData', {}).get('INDUSTRY', [])
            for ind in industries:
                if ind.get('sector', '').lower() == sector_name.lower():
                    banking_ids = list(ind.get('industries', {}).keys())
                    break
        except Exception as e:
            logger.error(f"Failed to parse sector mapping: {e}")
            
    if not banking_ids:
        logger.warning(f"Could not map sector '{sector_name}' to any industry IDs.")
        return []
        
    # Query the internal API unpaginated
    url_api = "https://groww.in/v1/api/stocks_data/v1/all_stocks"
    api_headers = {
        "User-Agent": headers["User-Agent"],
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
      "size": "500",  # Safely bypass the standard 15/20 limit visually enforced via React
      "sortBy": "NA",
      "sortType": "ASC"
    }
    
    r2 = requests.post(url_api, headers=api_headers, json=payload)
    if r2.status_code != 200:
        logger.error(f"Internal structure API failure: {r2.status_code}")
        return []
        
    try:
        resp = r2.json()
        records = resp.get('records', [])
        logger.info(f"Successfully fetched {len(records)} unpaginated records for sector {sector_name}")
        return records
    except Exception as e:
        logger.error(f"Failed to parse internal JSON stocks: {e}")
        return []

if __name__ == "__main__":
    banking_stocks = get_sector_stocks("Banking")
    print("\nSAMPLE BANKING STOCKS:")
    for stock in banking_stocks[:3]:
        print(f"- {stock.get('companyName')} (Symbol: {stock.get('searchId')}) | Close: {stock.get('closePrice')}")
