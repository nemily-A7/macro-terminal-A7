import requests
from terminal1_macro.data.settings import settings
import sys

key = settings.trading_economics_api_key
print(f"Key: {key}")

url = "https://api.tradingeconomics.com/historical/country/Euro Area/indicator/Inflation Rate"
params = {
    "c": key,
    "f": "json",
    "d1": "2020-01-01"
}
resp = requests.get(url, params=params)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

if resp.status_code == 200 and resp.json():
    print("Success!")
else:
    print("Fail")
