from fastapi import APIRouter, HTTPException
import requests
import json
from bs4 import BeautifulSoup
from .mf_fetcher import get_sector_mfs
import sys
import os

# Appending root directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger("mutual_funds_router")

router = APIRouter(prefix="/api/mutual-funds", tags=["mutual-funds"])

POPULAR_MF_CATEGORIES = ["Equity", "Debt", "Hybrid", "Index Funds"]

@router.get("/categories")
def list_mf_categories():
    """List all available predefined Mutual Fund categories."""
    logger.info("Fetching mutual fund categories")
    return {"categories": POPULAR_MF_CATEGORIES}

@router.get("/category/{category_name}")
def get_mfs_in_category(category_name: str):
    """Get all mutual funds belonging to a specific category with details."""
    logger.info(f"Fetching mutual funds for category: {category_name}")
    mfs = get_sector_mfs(category_name)
    if not mfs:
        logger.error(f"No mutual funds found for category: {category_name}")
        raise HTTPException(status_code=404, detail=f"No mutual funds found for category: {category_name}")
    
    logger.info(f"Successfully retrieved {len(mfs)} mutual funds for category {category_name}")
    return {"category": category_name, "count": len(mfs), "mutual_funds": mfs}

@router.get("/{search_id}")
def get_individual_mf(search_id: str):
    """Get individual mutual fund details by scraping the specific Groww fund page."""
    logger.info(f"Fetching individual mutual fund details for: {search_id}")
    url = f"https://groww.in/mutual-funds/{search_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        logger.error(f"Failed to fetch mutual fund page {search_id}: Status {r.status_code}")
        raise HTTPException(status_code=r.status_code, detail=f"Failed to fetch mutual fund page: {search_id}")
        
    soup = BeautifulSoup(r.text, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if not script_tag:
        logger.error(f"Data structure __NEXT_DATA__ not found on mutual fund page for {search_id}")
        raise HTTPException(status_code=404, detail="Data structure not found on mutual fund page.")
        
    data = json.loads(script_tag.string)
    page_props = data.get('props', {}).get('pageProps', {})
    
    # Groww stores MF data here
    mf_info = page_props.get('mfServerSideData', {})
    if not mf_info:
        logger.warning(f"Could not find mfServerSideData for {search_id}. Returning raw props keys.")
        return {"raw_props_keys": list(page_props.keys())}
        
    logger.info(f"Successfully fetched details for mutual fund {search_id}")
    return {"search_id": search_id, "details": mf_info}
