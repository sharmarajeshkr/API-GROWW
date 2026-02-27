from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
from growwapi import GrowwAPI
from .sector_fetcher import get_sector_stocks, get_all_sectors
import sys
import os
import requests
from bs4 import BeautifulSoup
import json

# Appending root directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger("stocks_router")

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

# Initialize SDK Client for individual stock fetching
load_dotenv()
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
groww_client = None

if api_key and api_secret:
    try:
        access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
        groww_client = GrowwAPI(token=access_token)
        logger.info("Successfully initialized official Groww SDK")
    except Exception as e:
        logger.warning(f"Could not initialize official Groww SDK: {e}")

@router.get("/sectors")
def list_stock_sectors():
    """List all available Stock sectors directly fetched from Groww."""
    logger.info("Fetching all stock sectors dynamically")
    sectors = get_all_sectors()
    if not sectors:
        raise HTTPException(status_code=500, detail="Failed to fetch stock sectors from Groww")
    return {"count": len(sectors), "sectors": sectors}

@router.get("/sector/{sector_name}")
def get_stocks_in_sector(sector_name: str):
    """Get all stocks belonging to a specific sector with details."""
    logger.info(f"Fetching stocks for sector: {sector_name}")
    stocks = get_sector_stocks(sector_name)
    if not stocks:
        logger.error(f"No stocks found for sector: {sector_name}")
        raise HTTPException(status_code=404, detail=f"No stocks found for sector: {sector_name}")
    
    logger.info(f"Successfully retrieved {len(stocks)} stocks for sector {sector_name}")
    return {"sector": sector_name, "count": len(stocks), "stocks": stocks}

@router.get("/{trading_symbol}")
def get_individual_stock(trading_symbol: str):
    """Get individual stock details explicitly using the official Groww API."""
    logger.info(f"Fetching individual stock details for: {trading_symbol}")
    if not groww_client:
         logger.error("Groww API client not initialized.")
         raise HTTPException(status_code=500, detail="Groww API client not initialized.")
    try:
         # 1. Fetch Official Quote
         quote = groww_client.get_quote(
             trading_symbol=trading_symbol.upper(),
             exchange=GrowwAPI.EXCHANGE_NSE,
             segment=GrowwAPI.SEGMENT_CASH
         )
         
         # 2. Fetch Comprehensive Rich Data via Scrape
         rich_data = {}
         scrape_url = f"https://groww.in/stocks/{trading_symbol.lower()}"
         r = requests.get(scrape_url, headers={"User-Agent": "Mozilla/5.0"})
         if r.status_code == 200:
             soup = BeautifulSoup(r.text, 'html.parser')
             script_tag = soup.find('script', id='__NEXT_DATA__')
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
