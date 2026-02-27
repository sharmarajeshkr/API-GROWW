from fastapi import APIRouter, HTTPException
import httpx
import json
from bs4 import BeautifulSoup
from services.mf_scraper import get_sector_mfs
import sys
import os
from async_lru import alru_cache

# Appending root directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.logger import get_logger
from core.schemas import MFCategoryListResponse, MFListResponse, MFDetailResponse

logger = get_logger("mutual_funds_router")

router = APIRouter(prefix="/api/mutual-funds", tags=["mutual-funds"])

from core.database import AsyncSessionLocal
from core.models import MFCategory, MutualFund
from sqlalchemy.future import select

@router.get("/categories", response_model=MFCategoryListResponse)
async def list_mf_categories():
    """List all available predefined Mutual Fund categories dynamically from Database."""
    logger.info("Fetching mutual fund categories from Database")
    async with AsyncSessionLocal() as session:
        stmt = select(MFCategory.name)
        res = await session.execute(stmt)
        categories = res.scalars().all()
        
    return {"categories": list(categories) if categories else []}

@router.get("/category/{category_name}", response_model=MFListResponse)
async def get_mfs_in_category(category_name: str):
    """Get all mutual funds belonging to a specific category from Database."""
    logger.info(f"Fetching mutual funds for category: {category_name} (from DB)")
    async with AsyncSessionLocal() as session:
        stmt = select(MFCategory).where(MFCategory.name == category_name)
        res = await session.execute(stmt)
        cat_obj = res.scalars().first()
        
        if not cat_obj:
            logger.error(f"Category not found in DB: {category_name}")
            raise HTTPException(status_code=404, detail=f"No mutual funds found for category: {category_name}")
            
        stmt_mfs = select(MutualFund).where(MutualFund.category_id == cat_obj.id)
        res_mfs = await session.execute(stmt_mfs)
        db_mfs = res_mfs.scalars().all()
        
        # Serialize to match expected Pydantic schema
        formatted_mfs = []
        for mf in db_mfs:
            formatted_mfs.append({
                "search_id": mf.search_id,
                "schemeName": mf.scheme_name,
                "return3y": mf.return_3y,
                "return5y": mf.return_5y
            })
    
    if not formatted_mfs:
        raise HTTPException(status_code=404, detail=f"No mutual funds found for category: {category_name}")
        
    logger.info(f"Successfully retrieved {len(formatted_mfs)} mutual funds for category {category_name}")
    return {"category": category_name, "count": len(formatted_mfs), "mutual_funds": formatted_mfs}

@router.get("/{search_id}", response_model=MFDetailResponse)
async def get_individual_mf(search_id: str):
    """Get individual mutual fund details by scraping the specific Groww fund page."""
    logger.info(f"Fetching individual mutual fund details for: {search_id}")
    url = f"https://groww.in/mutual-funds/{search_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(url, headers=headers)
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
        
        # Groww stores MF data in mfServerSideData
        mf_info = page_props.get('mfServerSideData', {})
        if not mf_info:
            logger.warning(f"Could not find rich 'mfServerSideData' data for {search_id}. Returning raw props keys.")
            return {
                "search_id": search_id,
                "basic_details": {},
                "comprehensive_details": {},
                "raw_props_keys": list(page_props.keys())
            }
            
        rich_data = {
             "returns": mf_info.get("return_stats", []),
             "holdings": mf_info.get("holdings", []),
             "fund_manager": mf_info.get("other_details", {}).get("fund_manager", "Unknown"),
             "pros_cons": mf_info.get("pros_cons", {}),
             "amc_info": mf_info.get("amc", {})
        }
            
        logger.info(f"Successfully fetched deep comprehensive details for mutual fund {search_id}")
        return {
            "search_id": search_id, 
            "basic_details": mf_info.get('search_option', {}),
            "comprehensive_details": rich_data
        }
