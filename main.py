import os
import asyncio
from dotenv import load_dotenv
from growwapi import GrowwAPI
from services.stock_scraper import get_sector_stocks
from services.mf_scraper import get_sector_mfs  

load_dotenv()

# Get credentials from environment
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")

if not api_key or not api_secret:
    print("Error: API_KEY or API_SECRET not found in environment.")
    exit(1)

async def main():
    try:
        print("Authenticating with Groww API...")
        # Step 1: Generate an access token using API key and secret
        access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
        print("Successfully generated access token.")
        
        if not access_token:
            print(f"Error: Could not retrieve access token.")
            exit(1)
            
        # Step 2: Initialize client
        groww_client = GrowwAPI(token=access_token)
        
        print("Successfully formatted token. Fetching profile details...")
        profile = groww_client.get_user_profile()
        print(profile)
        
        print("\n--- 1. Fetching Stocks in the 'Banking' Sector ---")
        
        banking_stocks = await get_sector_stocks("Banking")
        if banking_stocks:
            print(f"Total Banking Stocks Found: {len(banking_stocks)}")
            print("Top 3 Banking Stocks:")
            for stock in banking_stocks[:3]:
                print(f"  - {stock.get('companyName')} (Symbol: {stock.get('searchId')}) | Close Price: Rs. {stock.get('closePrice')}")
                
        print("\n--- 2. Fetching Mutual Funds in the 'Equity' Category ---")
        
        equity_mfs = await get_sector_mfs("Equity")
        if equity_mfs:
            print(f"Total Equity Mutual Funds Found: {len(equity_mfs)}")
            print("Top 3 Equity Mutual Funds:")
            for mf in equity_mfs[:3]:
                name = mf.get('search_id') or mf.get('schemeName') or mf.get('title')
                print(f"  - {name} | 3Y Return: {mf.get('return3y')}%")
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
