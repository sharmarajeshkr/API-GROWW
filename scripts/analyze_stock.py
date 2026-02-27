import requests
from bs4 import BeautifulSoup
import json

def analyze_hdfc_bank():
    print("Fetching HDFC Bank rich JSON data...")
    url = "https://groww.in/stocks/hdfc-bank-ltd"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    soup = BeautifulSoup(r.text, 'html.parser')
    tag = soup.find('script', id='__NEXT_DATA__')
    
    data = json.loads(tag.string)
    stock_data = data.get('props', {}).get('pageProps', {}).get('stockData', {})
    
    # 1. Overview / Stats
    stats = stock_data.get('stats', {})
    print(f"\n[STATS / OVERVIEW Module] (Keys: {len(stats)})")
    for k, v in list(stats.items())[:5]:
        print(f" - {k}: {v}")
        
    # 2. Fundamentals
    fundamentals = stock_data.get('fundamentals', {})
    print(f"\n[FUNDAMENTALS Module] (Keys: {len(fundamentals)})")
    if isinstance(fundamentals, dict):
        for k, v in list(fundamentals.items())[:5]:
            print(f" - {k}: {v}")
            
    # 3. Financials
    financials = stock_data.get('financialStatementV2', [])
    print(f"\n[FINANCIALS Module] (Years found: {len(financials)})")
    if financials and isinstance(financials, list):
         print(f" Sample Year block keys: {financials[0].keys()}")
         print(f" Sample Title: {financials[0].get('financialParticularTitle')}")
         
    # 4. Technicals (Sometimes loaded separately)
    tech = data.get('props', {}).get('pageProps', {}).get('stocksTechnicalsData', {})
    if tech:
         print(f"\n[TECHNICALS] Keys: {tech.keys()}")
    else:
         print("\n[TECHNICALS] not found directly in SSR cache.")

if __name__ == "__main__":
    analyze_hdfc_bank()
