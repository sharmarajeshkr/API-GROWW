import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

# Add root directory to python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_api import app

@pytest.mark.anyio
async def test_list_stock_sectors():
    """Verify that we can retrieve the static list of stock sectors."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/stocks/sectors")
    assert response.status_code == 200
    data = response.json()
    assert "sectors" in data
    assert isinstance(data["sectors"], list)
    assert len(data["sectors"]) > 0
    assert "Banking" in data["sectors"]

@pytest.mark.anyio
async def test_get_stocks_in_sector():
    """Verify that we can fetch real sector data directly from psycopg2/Neon integration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/stocks/sector/Banking")
    assert response.status_code == 200
    data = response.json()
    assert data["sector"] == "Banking"
    assert "count" in data
    assert "stocks" in data
    assert len(data["stocks"]) > 0
    # verify it has expected DB details like companyName
    assert "companyName" in data["stocks"][0]
    assert "searchId" in data["stocks"][0]

@pytest.mark.anyio
async def test_get_individual_stock():
    """Verify official Groww API authentication works by pulling a real quote for RELIANCE."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=10.0) as ac:
        response = await ac.get("/api/stocks/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "RELIANCE"
    assert "live_quote" in data
    assert "comprehensive_details" in data
    details = data["live_quote"]
    # Check for keys returned by the official API
    assert "day_change" in details or "market_cap" in details or "upper_circuit_limit" in details
    
    # Check for rich stats injected by the scraper
    rich = data["comprehensive_details"]
    assert "overview_stats" in rich
    assert "financials" in rich

@pytest.mark.anyio
async def test_list_mf_categories():
    """Verify that we can retrieve the synced list of mutual fund categories from the DB."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/mutual-funds/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) > 0
    assert "Equity" in data["categories"]

@pytest.mark.anyio
async def test_get_mfs_in_category():
    """Verify that we can fetch real category data for Mutual funds from the DB."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/mutual-funds/category/Equity")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Equity"
    assert "count" in data
    assert "mutual_funds" in data
    assert len(data["mutual_funds"]) > 0
    # Ensure scheme names are present
    first_mf = data["mutual_funds"][0]
    assert "schemeName" in first_mf or "search_id" in first_mf or "title" in first_mf

@pytest.mark.anyio
async def test_get_individual_mf():
    """Verify we can fetch deep nested details for an individual mutual fund."""
    test_id = "bandhan-small-cap-fund-direct-growth"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=10.0) as ac:
        response = await ac.get(f"/api/mutual-funds/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["search_id"] == test_id
    assert "basic_details" in data
    assert "comprehensive_details" in data
    
    # Check for rich elements injected by the scraper
    rich = data["comprehensive_details"]
    assert "returns" in rich
    assert "fund_manager" in rich
    assert "holdings" in rich
