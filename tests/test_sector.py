import os
from dotenv import load_dotenv
from growwapi import GrowwAPI

load_dotenv()
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")

access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
client = GrowwAPI(token=access_token)
try:
    instruments = client.get_all_instruments()
    print(instruments.head(2))
    print("Columns:", instruments.columns.tolist() if hasattr(instruments, "columns") else "Not a DataFrame")
except Exception as e:
    print("Error:", e)
