import requests
import json
import time
import subprocess

# Start the server in the background
print("Starting Uvicorn server...")
proc = subprocess.Popen(["venv\\Scripts\\python.exe", "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"])
time.sleep(3) # wait for server to start

try:
    BASE_URL = "http://127.0.0.0:8000"
    # Helper to print response
    def check(url):
        r = requests.get(f"http://127.0.0.1:8000{url}")
        print(f"\n--- GET {url} [{r.status_code}] ---")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2)[:300] + "...")
        else:
            print("Error:", r.text)

    # test 1
    check("/api/stocks/sectors")
    
    # test 2
    check("/api/stocks/sector/Banking")
    
    # test 3
    check("/api/stocks/RELIANCE")
    
    # test 4
    check("/api/mutual-funds/categories")
    
    # test 5
    check("/api/mutual-funds/category/Equity")
    
    # test 6
    check("/api/mutual-funds/bandhan-small-cap-fund-direct-growth")

finally:
    print("\nShutting down server...")
    proc.terminate()
