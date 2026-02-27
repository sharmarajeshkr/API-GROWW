from fastapi import APIRouter, HTTPException, Depends
import os
import time
from dotenv import load_dotenv
from growwapi import GrowwAPI
from services.stock_scraper import get_sector_stocks, get_all_sectors
import sys
import httpx
from bs4 import BeautifulSoup
import json

# Appending root directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.logger import get_logger
from core.schemas import SectorListResponse, StockListResponse, StockDetailResponse

logger = get_logger("stocks_router")

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

# Initialize SDK Client dynamically with a Token Refresh Dependency
load_dotenv()
_groww_client = None
_token_expiry = 0

def get_groww_client():
    global _groww_client, _token_expiry
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    
    if not api_key or not api_secret:
        return None
        
    current_time = time.time()
    # Refresh token if missing or if it's older than 12 hours (43200 seconds)
    if _groww_client is None or current_time > _token_expiry:
        try:
            access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
            _groww_client = GrowwAPI(token=access_token)
            _token_expiry = current_time + 40000 
            logger.info("Successfully initialized/refreshed official Groww SDK")
        except Exception as e:
            logger.warning(f"Could not initialize official Groww SDK: {e}")
            return None
            
    return _groww_client

@router.get("/sectors", response_model=SectorListResponse)
async def list_stock_sectors():
    """List all available Stock sectors directly fetched from Groww."""
    logger.info("Fetching all stock sectors dynamically")
    sectors = await get_all_sectors()
    if not sectors:
        raise HTTPException(status_code=500, detail="Failed to fetch stock sectors from Groww")
    return {"count": len(sectors), "sectors": sectors}

@router.get("/sector/{sector_name}", response_model=StockListResponse)
async def get_stocks_in_sector(sector_name: str):
    """Get all stocks belonging to a specific sector with details."""
    logger.info(f"Fetching stocks for sector: {sector_name}")
    stocks = await get_sector_stocks(sector_name)
    if not stocks:
        logger.error(f"No stocks found for sector: {sector_name}")
        raise HTTPException(status_code=404, detail=f"No stocks found for sector: {sector_name}")
    
    logger.info(f"Successfully retrieved {len(stocks)} stocks for sector {sector_name}")
    return {"sector": sector_name, "count": len(stocks), "stocks": stocks}

@router.get("/{trading_symbol}", response_model=StockDetailResponse)
async def get_individual_stock(trading_symbol: str, client: GrowwAPI = Depends(get_groww_client)):
    """Get individual stock details explicitly using the official Groww API."""
    logger.info(f"Fetching individual stock details for: {trading_symbol}")
    if not client:
         logger.error("Groww API client not initialized.")
         raise HTTPException(status_code=500, detail="Groww API client not initialized.")
    try:
         # 1. Fetch Official Quote (this part is synchronous, it's fine for the fast official SDK, or could be run in a threadpool)
         import asyncio
         loop = asyncio.get_running_loop()
         quote = await loop.run_in_executor(None, lambda: client.get_quote(
             trading_symbol=trading_symbol.upper(),
             exchange=GrowwAPI.EXCHANGE_NSE,
             segment=GrowwAPI.SEGMENT_CASH
         ))
         
         # 2. Fetch Comprehensive Rich Data via Async Scrape
         rich_data = {}
         search_slug = "reliance-industries-ltd" if trading_symbol.upper() == "RELIANCE" else trading_symbol.lower()
         scrape_url = f"https://groww.in/stocks/{search_slug}"
         
         async with httpx.AsyncClient(follow_redirects=True) as async_client:
             r = await async_client.get(scrape_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
             logger.warning(f"URL FETCHED: {r.url} STATUS: {r.status_code}")
             if r.status_code == 200:
                 soup = BeautifulSoup(r.text, 'html.parser')
                 script_tag = soup.find('script', id='__NEXT_DATA__')
                 logger.warning(f"script_tag found: {script_tag is not None}")
                 if script_tag:
                     data = json.loads(script_tag.string)
                     stock_data = data.get('props', {}).get('pageProps', {}).get('stockData', {})
                     
                     rich_data = {
                         "overview_stats": stock_data.get('stats', {}),
                         "fundamentals": stock_data.get('fundamentals', {}),
                         "financials": stock_data.get('financialStatementV2', []),
                         "shareholding": stock_data.get('shareHoldingPattern', {}),
                         "similar_assets": stock_data.get('similarAssets', [])
                     }
                     
                     # Enforce dict casting to prevent json serialization type errors
                     if not isinstance(rich_data["fundamentals"], dict):
                          rich_data["fundamentals"] = {}
                 
         logger.info(f"Successfully fetched unified quote & rich data for {trading_symbol}")
         return {
             "symbol": trading_symbol.upper(),
             "live_quote": quote,
             "comprehensive_details": rich_data
         }
    except Exception as e:
         logger.error(f"Failed to fetch {trading_symbol}: {str(e)}")
         raise HTTPException(status_code=400, detail=f"Failed to fetch {trading_symbol}: {str(e)}")
