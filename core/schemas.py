from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- Shared Schemas ---
# (Add shared models here if any)

# --- Stock Schemas ---
class SectorListResponse(BaseModel):
    count: int
    sectors: List[str]

class StockListResponse(BaseModel):
    sector: str
    count: int
    stocks: List[Dict[str, Any]]  # Keeping it flexible since internal API returns vary

class StockDetailResponse(BaseModel):
    symbol: str
    live_quote: Dict[str, Any]
    comprehensive_details: Dict[str, Any]

# --- Mutual Fund Schemas ---
class MFCategoryListResponse(BaseModel):
    categories: List[str]

class MFListResponse(BaseModel):
    category: str
    count: int
    mutual_funds: List[Dict[str, Any]] # Keeping it flexible

class MFDetailResponse(BaseModel):
    search_id: str
    basic_details: Dict[str, Any]
    comprehensive_details: Dict[str, Any]
    raw_props_keys: Optional[List[str]] = None
