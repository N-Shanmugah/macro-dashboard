import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
import os

# ---------------------------------------------------------------
# CENTRAL BANK POLICY RATES DASHBOARD
# Panels: Single panel — US, UK, ECB, Japan (left axis, %)
#                        Singapore S$NEER (right axis, index)
# Lookback: 60 months (5 years), monthly data
# Data source: FRED API + MAS S$NEER xlsx
# Style: Bloomberg dark
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------
BG    = "#0A0A0A"
PANEL = "#111111"
TEXT  = "#D0D0D0"
GRID  = "#2A2A2A"
SPINE = "#333333"

C_US   = "#4DA6FF"   # bright blue   — Federal Reserve
C_UK   = "#FF4D4D"   # bright red    — Bank of England
C_ECB  = "#FFD700"   # gold/yellow   — European Central Bank
C_JP   = "#66FF99"   # mint green    — Bank of Japan
C_NEER = "#FF99FF"   # soft magenta  — S$NEER (secondary axis)

# ---------------------------------------------------------------
# Guard: ensure FRED API key is set before anything runs.
# ---------------------------------------------------------------
api_key = os.environ.get("FRED_API_KEY")
if not api_key:
    raise EnvironmentError(
        "FRED_API_KEY not found in environment variables. "
        "Set it before running this script."
    )

fred = Fred(api_key=api_key)

# ---------------------------------------------------------------
# 60-month lookback window.
# ---------------------------------------------------------------
end_date   = pd.Timestamp.today()
start_date = end_date - pd.DateOffset(months=60)

# ---------------------------------------------------------------
# Fetch central bank policy rates from FRED.
# Each country has a list of candidate series IDs tried in order.
# The first one that exists and returns data is used.
#
# Some FRED series are daily (e.g. ECBDFR). These are resampled
# to month-end so all lines share the same x-axis frequency.
#
# forward-fill handles sparse series where FRED stores NaN between
# policy change dates (common for Japan at the zero lower bound).
# ---------------------------------------------------------------
print("Fetching central bank policy rates from FRED...")

series_candidates = {
    "US (Fed)"   : (["FEDFUNDS"],                                             C_US),
    "UK (BoE)"   : (["BOEUKRAM156N", "BOERUKM", "IUDSOIA"],                  C_UK),
    "ECB"        : (["ECBDFR", "ECBMLFR"],                                    C_ECB),
    "Japan (BoJ)": (["IR3TIB01JPM156N", "IRSTCB01JPM156N", "INTDSRJPM193N"], C_JP),
}

def fetch_first_available(fred_client, candidates, start, end):
    """Try each series ID in order; return (series_id, Series) for the first hit."""
    for sid in candidates:
        try:
            raw = fred_client.get_series(sid, observation_start=start, observation_end=end)
            series = raw.ffill().dropna()
            # resample daily series to month-end so all lines align
            if len(series) > 100:
                series = series.resample("ME").last()
            if not series.empty:
                return sid, series
            print(f"    {sid}: exists but no data in range — trying next")
        except ValueError:
            print(f"    {sid}: series not found on FRED — trying next")
    return None, None

rates = {}
for label, (candidates, _) in series_candidates.items():
    print(f"  Fetching {label}...")
    sid, series = fetch_first_available(fred, candidates, start_date, end_date)
    if series is None:
        print(f"    WARNING: No valid series found for {label} — skipping.")
        continue
    rates[label] = series
    print(f"    Using {sid} | {len(series)} observations | Latest: {series.iloc[-1]:.2f}%")

# ---------------------------------------------------------------
# Load S$NEER from MAS xlsx file.
# MAS publishes this as a weekly index (Jan 1999 = 100).
# We resample to month-end to align with the rates series.
# ---------------------------------------------------------------
print("Loading S$NEER from file...")
neer_path = os.path.join(os.path.dirname(__file__), "S$NEER.xlsx")
neer_raw = pd.read_excel(neer_path, sheet_name="Sheet 0")
neer_raw.columns = ["date", "neer"]
neer_raw["date"] = pd.to_datetime(neer_raw["date"])
neer_raw = neer_raw.set_index("date").sort_index()

# resample weekly → monthly (last observation of each month)
neer_monthly = neer_raw["neer"].resample("ME").last()
neer = neer_monthly[(neer_monthly.index >= start_date) & (neer_monthly.index <= end_date)]
print(f"  S$NEER: {len(neer)} monthly observations | Latest: {neer.iloc[-1]:.2f}")

print("Building chart...")

# ---------------------------------------------------------------
# Build figure — single panel with two y-axes.
# ax  = left axis  — policy rates in % per annum
# ax2 = right axis — S$NEER index (Jan 1999 = 100)
# twinx() creates a second axis that shares the same x-axis
# but has an independent y-axis on the right side.
# ---------------------------------------------------------------
fig, ax = plt.subplots(1, 1, figsize=(13, 7))
fig.patch.set_facecolor(BG)
ax2 = ax.twinx()

# ---------------------------------------------------------------
# Dashboard header
# ---------------------------------------------------------------
fig.text(0.5, 0.96,
         "CENTRAL BANK POLICY RATES  &  S$NEER",
         ha="center", fontsize=13, fontweight="bold", color=TEXT)

fig.text(0.5, 0.935,
         f"60-Month View  |  {start_date.strftime('%b %Y')} – {end_date.strftime('%b %Y')}"
         f"  |  US · UK · ECB · Japan (left)  ·  S$NEER index (right)",
         ha="center", fontsize=9, color="#888888")

# ---------------------------------------------------------------
# LEFT AXIS — plot each central bank rate.
# Annotate the latest value at the end of each line.
# ---------------------------------------------------------------
for label, (candidates, colour) in series_candidates.items():
    if label not in rates:
        continue
    series = rates[label]
    ax.plot(series.index, series.values,
            color=colour, linewidth=1.8, label=label, zorder=3)
    ax.annotate(f"  {series.iloc[-1]:.2f}%",
                xy=(series.index[-1], series.iloc[-1]),
                fontsize=8.5, color=colour, va="center", fontweight="bold")

# zero reference line — relevant for Japan near the lower bound
ax.axhline(y=0, color=SPINE, linewidth=0.8, linestyle="--", alpha=0.7)

# ---------------------------------------------------------------
# RIGHT AXIS — plot S$NEER index.
# Dashed line so it reads clearly as a different type of series.
# A rising NEER = SGD appreciating = MAS tightening policy.
# Annotate the latest index value on the right side.
# ---------------------------------------------------------------
ax2.plot(neer.index, neer.values,
         color=C_NEER, linewidth=1.6, linestyle="--",
         label="S$NEER (MAS, right)", zorder=3)

ax2.annotate(f"{neer.iloc[-1]:.1f}  ",
             xy=(neer.index[-1], neer.iloc[-1]),
             fontsize=8.5, color=C_NEER, va="center", fontweight="bold",
             ha="right")

# ---------------------------------------------------------------
# Style the left axis (ax) — Bloomberg dark.
# ---------------------------------------------------------------
ax.set_facecolor(PANEL)
ax.tick_params(colors=TEXT, labelsize=8)
ax.yaxis.label.set_color(TEXT)
ax.title.set_color(TEXT)
ax.grid(True, color=GRID, linewidth=0.6, alpha=1.0)
for side in ("top",):
    ax.spines[side].set_visible(False)
for side in ("bottom", "left"):
    ax.spines[side].set_color(SPINE)

ax.set_title("Policy Rate (%) vs S$NEER Index", fontsize=10, fontweight="bold", pad=8)
ax.set_ylabel("Rate — % per annum (left)", fontsize=8, labelpad=6)

# ---------------------------------------------------------------
# Style the right axis (ax2) — match Bloomberg dark.
# The right spine is kept visible and coloured to match NEER.
# ---------------------------------------------------------------
ax2.tick_params(colors=C_NEER, labelsize=8)
ax2.yaxis.label.set_color(C_NEER)
ax2.set_ylabel("S$NEER Index — Jan 1999 = 100 (right)", fontsize=8,
               labelpad=6, color=C_NEER)
ax2.spines["right"].set_color(C_NEER)
ax2.spines["top"].set_visible(False)

# ---------------------------------------------------------------
# Combined legend — pull handles from both axes so all five
# series appear in one legend box.
# ---------------------------------------------------------------
handles_left,  labels_left  = ax.get_legend_handles_labels()
handles_right, labels_right = ax2.get_legend_handles_labels()
ax.legend(handles_left + handles_right, labels_left + labels_right,
          loc="upper left", fontsize=8,
          facecolor=PANEL, edgecolor=SPINE, labelcolor=TEXT)

# ---------------------------------------------------------------
# X-axis: tick every 6 months — 60 months = 10 ticks, readable.
# extend right edge by 3 months so end-of-line annotations
# on the left side are not clipped.
# ---------------------------------------------------------------
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8, color=TEXT)

ax.set_xlim(start_date, end_date + pd.DateOffset(months=3))

fig.subplots_adjust(top=0.88, bottom=0.10, left=0.07, right=0.93)

plt.show()
print("Done.")
