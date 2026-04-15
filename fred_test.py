import os
from fredapi import Fred

# --- Read the API key from Windows environment variables ---
# os.environ is a dictionary of all environment variables on your system.
# .get() returns None (instead of crashing) if the key doesn't exist.
api_key = os.environ.get("FRED_API_KEY")

# Guard: if the key is missing, print a clear message and stop.
# This usually means VS Code was open before the variable was saved —
# close and reopen VS Code entirely to fix it.
if not api_key:
    print("ERROR: FRED_API_KEY not found in environment variables.")
    print("Fix: close VS Code completely and reopen it, then run this script again.")
    exit(1)

print(f"FRED_API_KEY loaded successfully. (ends in ...{api_key[-4:]})\n")

# --- Connect to FRED ---
# Fred() takes your API key and creates a connection object.
# All data pulls go through this object.
fred = Fred(api_key=api_key)

# --- Pull Series 1: US 10-Year Treasury Yield ---
# Series ID: DGS10 — daily yield on 10-year US government bonds.
# This is one of the most-watched macro indicators globally.
print("--- US 10-Year Treasury Yield (DGS10) ---")
dgs10 = fred.get_series("DGS10")   # returns a pandas Series, indexed by date
print(dgs10.dropna().tail(5).to_string())  # show last 5 non-null values
print()

# --- Pull Series 2: Federal Funds Effective Rate ---
# Series ID: FEDFUNDS — the overnight lending rate set by the Fed.
# Drives borrowing costs across the entire economy.
print("--- Federal Funds Effective Rate (FEDFUNDS) ---")
fedfunds = fred.get_series("FEDFUNDS")
print(fedfunds.dropna().tail(5).to_string())
print()

print("Done. FRED API is working correctly.")
