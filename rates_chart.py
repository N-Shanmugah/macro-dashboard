import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred

# ---------------------------------------------------------------
# Load FRED API key from Windows environment variables.
# This is the same approach used in fred_test.py.
# ---------------------------------------------------------------
api_key = os.environ.get("FRED_API_KEY")

if not api_key:
    print("ERROR: FRED_API_KEY not found in environment variables.")
    print("Fix: close VS Code completely and reopen it, then run this script again.")
    exit(1)

fred = Fred(api_key=api_key)

# ---------------------------------------------------------------
# Fetch all five series from FRED.
# Each call returns a pandas Series indexed by date.
#
# FEDFUNDS  — Federal Funds Effective Rate (monthly, %)
# DGS2      — 2-Year Treasury Constant Maturity Rate (daily, %)
# DGS5      — 5-Year Treasury Constant Maturity Rate (daily, %)
# DGS10     — 10-Year Treasury Constant Maturity Rate (daily, %)
# DGS30     — 30-Year Treasury Constant Maturity Rate (daily, %)
# ---------------------------------------------------------------
print("Fetching data from FRED...")

fedfunds = fred.get_series("FEDFUNDS").dropna()
dgs2     = fred.get_series("DGS2").dropna()
dgs5     = fred.get_series("DGS5").dropna()
dgs10    = fred.get_series("DGS10").dropna()
dgs30    = fred.get_series("DGS30").dropna()

print("Data loaded. Opening chart window...")

# ---------------------------------------------------------------
# Limit historical data to the last 5 years.
# We calculate a cutoff date (today minus 5 years) and filter
# the Series to only rows where the index date is on or after it.
# ---------------------------------------------------------------
cutoff = pd.Timestamp.today() - pd.DateOffset(years=5)
fedfunds_5y = fedfunds[fedfunds.index >= cutoff]
dgs10_5y    = dgs10[dgs10.index >= cutoff]

# ---------------------------------------------------------------
# Calculate the 2Y-10Y spread.
# This is 10-Year yield minus 2-Year yield.
# When negative, the curve is "inverted" — short-term rates are
# higher than long-term rates — a historically reliable recession signal.
#
# pandas .align() ensures both series share the same dates before
# subtracting, since DGS2 and DGS10 may have slightly different
# trading day coverage. "inner" means keep only dates present in both.
# ---------------------------------------------------------------
dgs10_aligned, dgs2_aligned = dgs10.align(dgs2, join="inner")
spread = dgs10_aligned - dgs2_aligned
spread_5y = spread[spread.index >= cutoff]

# ---------------------------------------------------------------
# Snapshot: get the most recent value for each tenor.
# This gives us one point per maturity — used to draw the yield curve.
# ---------------------------------------------------------------
latest_date = dgs10.index[-1].strftime("%d %b %Y")

curve_tenors = ["2Y", "5Y", "10Y", "30Y"]
curve_values = [
    dgs2.iloc[-1],
    dgs5.iloc[-1],
    dgs10.iloc[-1],
    dgs30.iloc[-1],
]

# ---------------------------------------------------------------
# Build the chart window.
# fig = the entire figure (window)
# ax1, ax2 = the two individual chart panels (subplots)
# figsize = width x height in inches
# ---------------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 13))
fig.suptitle("US Interest Rates Dashboard", fontsize=14, fontweight="bold", y=0.99)

# ---------------------------------------------------------------
# CHART 1 (top panel): Fed Funds Rate vs 10-Year Treasury Yield
#
# This overlay shows whether the Fed's short-term rate is above or
# below the long-end yield — a key indicator of yield curve inversion.
# An inverted curve (Fed Funds > 10Y) historically precedes recessions.
# ---------------------------------------------------------------
ax1.plot(fedfunds_5y.index, fedfunds_5y.values, label="Fed Funds Rate (FEDFUNDS)",
         color="#e74c3c", linewidth=2)
ax1.plot(dgs10_5y.index, dgs10_5y.values, label="10-Year Treasury Yield (DGS10)",
         color="#2980b9", linewidth=2)

ax1.set_title("Fed Funds Rate vs 10-Year Treasury Yield (Last 5 Years)", fontsize=11)
ax1.set_ylabel("Rate (%)")
ax1.legend(loc="upper left", fontsize=9)
ax1.grid(True, alpha=0.3)

# Format the x-axis to show year labels cleanly
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax1.xaxis.set_major_locator(mdates.YearLocator())
fig.autofmt_xdate()

# ---------------------------------------------------------------
# CHART 2 (bottom panel): Current Yield Curve Snapshot
#
# The yield curve plots yield (%) against maturity (2Y, 5Y, 10Y, 30Y).
# A normal curve slopes upward — lenders demand more for longer duration.
# A flat or inverted curve signals stress in the credit/rate environment.
# ---------------------------------------------------------------
ax2.plot(curve_tenors, curve_values, marker="o", color="#27ae60",
         linewidth=2.5, markersize=8, markerfacecolor="white", markeredgewidth=2)

# Annotate each point with its exact yield value
for tenor, val in zip(curve_tenors, curve_values):
    ax2.annotate(f"{val:.2f}%", xy=(tenor, val),
                 xytext=(0, 10), textcoords="offset points",
                 ha="center", fontsize=9, color="#27ae60")

ax2.set_title(f"US Treasury Yield Curve — Snapshot as of {latest_date}", fontsize=11)
ax2.set_ylabel("Yield (%)")
ax2.set_xlabel("Maturity")
ax2.grid(True, alpha=0.3)

# Add a horizontal reference line at 0% — useful if rates go negative
ax2.axhline(y=0, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)

# ---------------------------------------------------------------
# CHART 3 (bottom panel): 2Y-10Y Treasury Spread
#
# Spread = 10-Year yield minus 2-Year yield.
# > 0  = normal curve (long rates > short rates)
# < 0  = inverted curve (short rates > long rates) — recession signal
#
# We shade the area below zero in red to make inversions visible
# at a glance. fill_between with "where=..." only fills the region
# where the condition is true.
# ---------------------------------------------------------------
ax3.plot(spread_5y.index, spread_5y.values, color="#8e44ad", linewidth=2,
         label="10Y - 2Y Spread")

# Shade negative region red (inversion)
ax3.fill_between(spread_5y.index, spread_5y.values, 0,
                 where=(spread_5y.values < 0),
                 color="#e74c3c", alpha=0.25, label="Inverted (recession signal)")

# Zero line
ax3.axhline(y=0, color="black", linewidth=0.8, linestyle="--", alpha=0.6)

ax3.set_title("2Y-10Y Treasury Spread (Last 5 Years)", fontsize=11)
ax3.set_ylabel("Spread (percentage points)")
ax3.legend(loc="upper right", fontsize=9)
ax3.grid(True, alpha=0.3)

# Same date formatting as ax1 so year labels align
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax3.xaxis.set_major_locator(mdates.YearLocator())

plt.tight_layout()
plt.show()

print("Done.")
