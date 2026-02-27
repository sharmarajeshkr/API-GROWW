import sys
import os

# Append current directory to path so it can find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stocks.sector_fetcher import get_all_sectors, get_sector_stocks

def verify_all_sectors():
    print("Fetching all sectors list...")
    sectors = get_all_sectors()
    print(f"Discovered {len(sectors)} sectors total.")
    
    empty_sectors = []
    error_sectors = []
    success_count = 0
    total_stocks_found = 0
    
    for idx, sector in enumerate(sectors):
        try:
            stocks = get_sector_stocks(sector)
            if not stocks:
                empty_sectors.append(sector)
            else:
                success_count += 1
                total_stocks_found += len(stocks)
                # Print every 10th sector to avoid console spam
                if success_count % 10 == 0:
                     print(f"[{idx+1}/{len(sectors)}] Verified '{sector}': Found {len(stocks)} stocks.")
        except Exception as e:
            error_sectors.append((sector, str(e)))
            
    print(f"\n--- Exhaustive Verification Results ---")
    print(f"Total Sectors Scanned: {len(sectors)}")
    print(f"Total Stocks Discovered Across All Sectors: {total_stocks_found}")
    print(f"Successfully fetched stock lists for: {success_count} sectors")
    print(f"Empty results for: {len(empty_sectors)} sectors")
    
    if empty_sectors:
        print(f"\nSectors with 0 stocks returned (may be empty on Groww or ID mapping failed):")
        print(empty_sectors)
        
    if error_sectors:
        print(f"\nSectors that threw code exceptions:")
        for err in error_sectors:
            print(f" - {err[0]}: {err[1]}")

if __name__ == "__main__":
    verify_all_sectors()
