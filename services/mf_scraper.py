import httpx
import urllib.parse
import sys
import os
from async_lru import alru_cache

# Appending root directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger import get_logger

logger = get_logger("mf_fetcher")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@alru_cache(maxsize=32)
async def get_sector_mfs(category="Equity"):
    """Fetches mutual fund names and details for a given category from Groww backend unpaginated API."""
    url = "https://groww.in/v1/api/search/v1/derived/scheme"
    
    # Try primary "category" first
    params = {
        "available_for_investment": "true",
        "category": category,
        "page": "0",
        "size": "500" # Bypass typical pagination locks
    }
    logger.debug(f"Fetching unpaginated MF schemas for {category}...")
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, params=params)
        
        if r.status_code != 200:
            logger.error(f"Failed to fetch internal MF JSON API: {r.status_code}")
            return []

        try:
            resp = r.json()
            content = resp.get('content', [])
            
            # If no results found, try "sub_category" for granular filters like "Large Cap" or "Liquid"
            if len(content) == 0:
                logger.debug(f"No results for primary category '{category}'. Retrying as sub_category...")
                fallback_params = {
                    "available_for_investment": "true",
                    "sub_category": category,
                    "page": "0",
                    "size": "500"
                }
                r_fallback = await client.get(url, headers=headers, params=fallback_params)
                if r_fallback.status_code == 200:
                    resp_fallback = r_fallback.json()
                    content = resp_fallback.get('content', [])
                    
            logger.info(f"Successfully fetched {len(content)} predefined MF records for term {category}")
            return content
        except Exception as e:
            logger.error(f"Failed to parse internal MF JSON: {e}")
            return []

if __name__ == "__main__":
    import asyncio
    async def main():
        equity_mfs = await get_sector_mfs("Equity")
        print("\nSAMPLE EQUITY MUTUAL FUNDS:")
        for mf in equity_mfs[:3]:
            name = mf.get('search_id') or mf.get('schemeName') or mf.get('title')
            print(f"- {name} | 3Y Return: {mf.get('return3y')}%")
    asyncio.run(main())
