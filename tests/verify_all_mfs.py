import sys
import os

# Append current directory to path so it can find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mutual_funds.router import POPULAR_MF_CATEGORIES
from mutual_funds.mf_fetcher import get_sector_mfs

def verify_all_mfs():
    # Currently the MF router uses a predefined list. Let's verify all of them.
    # We could also fetch dynamically like stocks, but let's test the active API list first.
    
    # We'll use an expanded exhaustive list of categories common on Groww
    categories = [
        "Equity", "Debt", "Hybrid", "Index Funds", "Solution Oriented", "Other",
        "Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "Multi Cap", "ELSS",
        "Liquid", "Ultra Short Duration", "Low Duration", "Money Market"
    ]
    
    # Merge with POPULAR_MF_CATEGORIES
    for cat in POPULAR_MF_CATEGORIES:
        if cat not in categories:
            categories.append(cat)
            
    print(f"Verifying {len(categories)} MF Categories...\n")
    
    empty_categories = []
    error_categories = []
    success_count = 0
    total_mfs_found = 0
    
    for idx, category in enumerate(categories):
        try:
            mfs = get_sector_mfs(category)
            if not mfs:
                empty_categories.append(category)
            else:
                success_count += 1
                total_mfs_found += len(mfs)
                print(f"[{idx+1}/{len(categories)}] Verified '{category}': Found {len(mfs)} Mutual Funds.")
        except Exception as e:
            error_categories.append((category, str(e)))
            
    print(f"\n--- MF Verification Results ---")
    print(f"Total Categories Scanned: {len(categories)}")
    print(f"Total MFs Discovered: {total_mfs_found}")
    print(f"Successfully fetched lists for: {success_count} categories")
    print(f"Empty results for: {len(empty_categories)} categories")
    
    if empty_categories:
        print(f"\nCategories with 0 MFs returned (may be invalid strings):")
        print(empty_categories)
        
    if error_categories:
        print(f"\nCategories throwing exceptions:")
        for err in error_categories:
            print(f" - {err[0]}: {err[1]}")

if __name__ == "__main__":
    verify_all_mfs()
