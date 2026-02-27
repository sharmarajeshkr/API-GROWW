import requests
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

def get_sector_mfs(category="Equity"):
    """Fetches mutual fund names and details for a given category from Groww backend unpaginated API."""
    url = "https://groww.in/v1/api/search/v1/derived/scheme"
    params = {
        "available_for_investment": "true",
        "category": category,
        "page": "0",
        "size": "500" # Bypass typical pagination locks
    }
    logger.debug(f"Fetching unpaginated MF schemas for {category}...")
    r = requests.get(url, headers=headers, params=params)
    
    if r.status_code != 200:
        logger.error(f"Failed to fetch internal MF JSON API: {r.status_code}")
        return []

    try:
        resp = r.json()
        content = resp.get('content', [])
        logger.info(f"Successfully fetched {len(content)} predefined MF records for category {category}")
        return content
    except Exception as e:
        logger.error(f"Failed to parse internal MF JSON: {e}")
        return []

if __name__ == "__main__":
    equity_mfs = get_sector_mfs("Equity")
    print("\nSAMPLE EQUITY MUTUAL FUNDS:")
    for mf in equity_mfs[:3]:
        name = mf.get('search_id') or mf.get('schemeName') or mf.get('title')
        print(f"- {name} | 3Y Return: {mf.get('return3y')}%")
