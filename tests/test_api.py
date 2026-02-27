import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add root directory to python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app

client = TestClient(app)

def test_list_stock_sectors():
    """Verify that we can retrieve the static list of stock sectors."""
    response = client.get("/api/stocks/sectors")
    assert response.status_code == 200
    data = response.json()
    assert "sectors" in data
    assert isinstance(data["sectors"], list)
    assert len(data["sectors"]) > 0
    assert "Banking" in data["sectors"]

def test_get_stocks_in_sector():
    """Verify that we can fetch real sector data from Groww's React state."""
    response = client.get("/api/stocks/sector/Banking")
    assert response.status_code == 200
    data = response.json()
    assert data["sector"] == "Banking"
    assert "count" in data
    assert "stocks" in data
    assert len(data["stocks"]) > 0
    # verify it has expected Groww details like companyName
    assert "companyName" in data["stocks"][0]
    assert "searchId" in data["stocks"][0]

def test_get_individual_stock():
    """Verify official Groww API authentication works by pulling a real quote for RELIANCE."""
    response = client.get("/api/stocks/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "RELIANCE"
    assert "details" in data
    details = data["details"]
    # Check for keys returned by the official API
    assert "day_change" in details or "market_cap" in details or "upper_circuit_limit" in details

def test_list_mf_categories():
    """Verify that we can retrieve the static list of mutual fund categories."""
    response = client.get("/api/mutual-funds/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) > 0
    assert "Equity" in data["categories"]

def test_get_mfs_in_category():
    """Verify that we can fetch real category data for Mutual funds."""
    response = client.get("/api/mutual-funds/category/Equity")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Equity"
    assert "count" in data
    assert "mutual_funds" in data
    assert len(data["mutual_funds"]) > 0
    # Ensure scheme names are present
    first_mf = data["mutual_funds"][0]
    assert "schemeName" in first_mf or "search_id" in first_mf or "title" in first_mf

def test_get_individual_mf():
    """Verify we can fetch deep nested details for an individual mutual fund."""
    test_id = "bandhan-small-cap-fund-direct-growth"
    response = client.get(f"/api/mutual-funds/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["search_id"] == test_id
    assert "details" in data
    # Ensure details is not just a key dump anymore
    assert "scheme_name" in data["details"] or "fund_name" in data["details"] or "amc_info" in data["details"] or "stp_details" in data["details"]
