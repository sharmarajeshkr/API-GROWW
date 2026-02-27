# Groww Data API

A robust, modular Python integration that effortlessly fetches rich Stock and Mutual Fund details straight from Groww. Built cleanly with **FastAPI** to easily serve endpoints and scale natively.

## 🌟 Features

- **Stock Sectors & Quotes:** Fetch stocks dynamically sorted by sector (e.g., "Banking", "IT"), or probe deep details for individual stocks using the official Groww API.
- **Mutual Fund Explorer:** Scrape categorization trees and deeply nested JSON React (`__NEXT_DATA__`) objects to retrieve performance metrics, AMC Info, and historical returns from Mutual Funds.
- **FastAPI Powered:** Everything is structured within APIRouters (`/api/stocks/...`, `/api/mutual-funds/...`) providing extreme speed and auto-generated Swagger UI (`/docs`).
- **Robust Centralized Logging:** Implemented with `logging.handlers.RotatingFileHandler`. All API queries, errors, and background scrapes are carefully tracked in `/logs/groww_api.log`.
- **Integrated Pytest Suite:** Complete coverage over all static lists, API queries, and web scraping hooks.

---

## 🚀 Getting Started

### 1. Requirements
Ensure you have `python` installed (Python 3.8+ recommended).

### 2. Environment Configuration
Create a `.env` file in the root directory. You will require Groww credentials to access official endpoints:
```env
API_KEY=your_groww_api_key_here
API_SECRET=your_groww_api_secret_here
```

### 3. Quickstart (Windows)

Simply double-click:
```bash
start_app.bat
```
This utility script handles everything for you: 
- Automatically checks for a `venv`.
- Detects if previous instances are stuck on Port 8000 and kills them.
- Boots the Uvicorn server natively.
- Opens your browser right to the interactive Swagger UI!

---

## 📡 API Endpoints 

### Stocks (`/api/stocks/...`)
- **`GET /sectors`** - Returns the main stock sector categories (Banking, IT, etc.)
- **`GET /sector/{sector_name}`** - Scrapes the Groww frontend to return exactly which stocks live under that sector grouping.
- **`GET /{trading_symbol}`** - Authenticates with the official Python SDK to fetch high-fidelity Market quotes (e.g. `RELIANCE`).

### Mutual Funds (`/api/mutual-funds/...`)
- **`GET /categories`** - Returns main MF filters (Equity, Debt, etc.)
- **`GET /category/{category_name}`** - Returns a list of all mutual funds under a sector.
- **`GET /{search_id}`** - Decodes server-side Next.js data to hand over deep properties of the specific fund.

---

## 🧪 Testing
The repository is bundled with a fully integrated testing suite hitting live endpoints through FastAPI's `TestClient`.

To execute:
```bash
pytest tests/test_api.py -v
```
Expect an all-green 100% pass verification on all major functionality endpoints!
