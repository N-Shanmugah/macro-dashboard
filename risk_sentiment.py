import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ---------------------------------------------------------------
# GLOBAL RISK SENTIMENT DASHBOARD
# Panels: VIX | DXY | Gold
# Lookback: 24 months, daily data
# Data source: Yahoo Finance (no API key required)
# Style: Bloomberg dark
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# Bloomberg-style dark colour palette.
# Defined once at the top so any colour change only needs editing here.
#
# BG     = figure background (outermost — the window border area)
# PANEL  = plot area background (inside the axes)
# TEXT   = all labels, titles, tick values
# GRID   = faint gridlines inside each panel
# SPINE  = the thin border lines around each panel
# ---------------------------------------------------------------
BG    = "#0A0A0A"
PANEL = "#111111"
TEXT  = "#D0D0D0"
GRID  = "#2A2A2A"
SPINE = "#333333"

# Line colours — chosen to pop on a dark background
C_VIX  = "#FF4D4D"   # bright red
C_DXY  = "#4DA6FF"   # bright blue
C_MA   = "#A0C8FF"   # lighter blue for the moving average
C_GOLD = "#FFD700"   # gold / amber

# ---------------------------------------------------------------
# Calculate 24-month lookback window.
# ---------------------------------------------------------------
end_date   = pd.Timestamp.today()
start_date = end_date - pd.DateOffset(months=24)

print("Fetching data from Yahoo Finance...")

# ---------------------------------------------------------------
# Download data. progress=False suppresses the yfinance progress bar.
# squeeze() converts a single-column DataFrame into a plain Series
# so standard maths operations (e.g. rolling mean) work correctly.
# ---------------------------------------------------------------
vix  = yf.download("^VIX",      start=start_date, end=end_date, auto_adjust=True, progress=False)["Close"].squeeze().dropna()
dxy  = yf.download("DX-Y.NYB",  start=start_date, end=end_date, auto_adjust=True, progress=False)["Close"].squeeze().dropna()
gold = yf.download("GC=F",      start=start_date, end=end_date, auto_adjust=True, progress=False)["Close"].squeeze().dropna()

print(f"VIX:  {len(vix)} days  | Latest: {vix.iloc[-1]:.2f}")
print(f"DXY:  {len(dxy)} days  | Latest: {dxy.iloc[-1]:.2f}")
print(f"Gold: {len(gold)} days  | Latest: ${gold.iloc[-1]:,.0f}")
print("Building chart...")

# ---------------------------------------------------------------
# 20-day moving average on DXY — smooths daily noise so the
# trend direction (up = risk-off, down = risk-on) is easier to read.
# ---------------------------------------------------------------
dxy_ma20 = dxy.rolling(20).mean()

# ---------------------------------------------------------------
# Build figure and 3 panel axes.
#
# figsize=(13, 13) — wide and square suits a landscape laptop screen.
# sharex=False     — each panel manages its own x-axis independently,
#                    avoiding the quirk where sharex collapses spacing.
# ---------------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 13), sharex=False)

# Apply dark background to the outer figure area
fig.patch.set_facecolor(BG)

# ---------------------------------------------------------------
# Main dashboard title.
# y=0.98 places it near the very top.
# pad below is controlled by subplots_adjust(top=) further down.
# ---------------------------------------------------------------
fig.suptitle(
    "Global Risk Sentiment  |  24-Month View",
    fontsize=13, fontweight="bold",
    color=TEXT, y=0.98
)

# ---------------------------------------------------------------
# Helper: apply Bloomberg-style dark formatting to an axes panel.
#
# This sets the background, removes the top/right border lines
# (cleaner look), colours the remaining spines, ticks, and labels.
# Called once per panel after all plotting is done.
# ---------------------------------------------------------------
def style_panel(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXT, labelsize=8)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=1.0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(SPINE)

# ---------------------------------------------------------------
# PANEL 1: VIX — CBOE Volatility Index (fear gauge)
#
# Reference lines mark the two key thresholds:
#   20 = boundary between calm and elevated
#   30 = stress / fear territory
#
# fill_between shades any period above 30 in translucent red,
# making fear spikes visible at a glance.
#
# The interpretation key is placed as small grey text inside
# the top of the panel — keeps the title line short and clean.
# ---------------------------------------------------------------
ax1.plot(vix.index, vix.values, color=C_VIX, linewidth=1.6, label="VIX", zorder=3)

ax1.fill_between(vix.index, vix.values, 30,
                 where=(vix.values > 30),
                 color=C_VIX, alpha=0.18, label="Extreme fear (>30)")

ax1.axhline(y=20, color="#FFA500", linewidth=0.9, linestyle="--", alpha=0.75, label="Caution (20)")
ax1.axhline(y=30, color=C_VIX,    linewidth=0.9, linestyle="--", alpha=0.75, label="Stress (30)")

# Current value — annotated just to the right of the last data point
ax1.annotate(f" {vix.iloc[-1]:.1f}",
             xy=(vix.index[-1], vix.iloc[-1]),
             fontsize=9, color=C_VIX, va="center", fontweight="bold")

ax1.set_title("VIX  —  Investor Fear Gauge", fontsize=10, fontweight="bold", pad=10)
ax1.set_ylabel("Level", fontsize=8, labelpad=6)
ax1.legend(loc="upper left", fontsize=7.5, facecolor=PANEL, edgecolor=SPINE, labelcolor=TEXT)
ax1.set_xlim(vix.index[0], vix.index[-1])

# Interpretation key inside the panel — small, unobtrusive
ax1.text(0.01, 0.05, "< 20  calm   |   20–30  caution   |   > 30  stress",
         transform=ax1.transAxes, fontsize=7, color="#888888", va="bottom")

style_panel(ax1)

# ---------------------------------------------------------------
# PANEL 2: DXY — ICE US Dollar Index
#
# Solid line = daily close.
# Dashed lighter line = 20-day moving average (trend direction).
#
# Rising DXY = investors buying USD safety (risk-off).
# Falling DXY = USD weakening, capital flowing to risk assets.
# ---------------------------------------------------------------
ax2.plot(dxy.index, dxy.values, color=C_DXY, linewidth=1.5, alpha=0.90, label="DXY", zorder=3)
ax2.plot(dxy_ma20.index, dxy_ma20.values, color=C_MA, linewidth=1.3,
         linestyle="--", label="20-Day MA", alpha=0.85)

ax2.annotate(f" {dxy.iloc[-1]:.2f}",
             xy=(dxy.index[-1], dxy.iloc[-1]),
             fontsize=9, color=C_DXY, va="center", fontweight="bold")

ax2.set_title("DXY  —  US Dollar Index", fontsize=10, fontweight="bold", pad=10)
ax2.set_ylabel("Level", fontsize=8, labelpad=6)
ax2.legend(loc="upper left", fontsize=7.5, facecolor=PANEL, edgecolor=SPINE, labelcolor=TEXT)
ax2.set_xlim(dxy.index[0], dxy.index[-1])

ax2.text(0.01, 0.05, "Rising = risk-off (USD strength)   |   Falling = risk-on",
         transform=ax2.transAxes, fontsize=7, color="#888888", va="bottom")

style_panel(ax2)

# ---------------------------------------------------------------
# PANEL 3: Gold — Safe Haven Demand (USD per troy ounce)
#
# Rising gold = risk-off, inflation fear, loss of confidence in
# equities or central bank credibility.
# Falling gold = risk-on, growth confidence, strong real yields.
#
# fill_between adds a faint amber glow under the line — this is
# purely visual and makes gold immediately recognisable as a panel.
# ---------------------------------------------------------------
ax3.plot(gold.index, gold.values, color=C_GOLD, linewidth=1.8, label="Gold futures (USD/oz)", zorder=3)

ax3.fill_between(gold.index, gold.values, gold.values.min() * 0.995,
                 color=C_GOLD, alpha=0.10)

ax3.annotate(f" ${gold.iloc[-1]:,.0f}",
             xy=(gold.index[-1], gold.iloc[-1]),
             fontsize=9, color=C_GOLD, va="center", fontweight="bold")

ax3.set_title("Gold  —  Safe Haven Demand", fontsize=10, fontweight="bold", pad=10)
ax3.set_ylabel("USD / oz", fontsize=8, labelpad=6)
ax3.legend(loc="upper left", fontsize=7.5, facecolor=PANEL, edgecolor=SPINE, labelcolor=TEXT)
ax3.set_xlim(gold.index[0], gold.index[-1])

ax3.text(0.01, 0.05, "Rising = risk-off / loss of confidence   |   Falling = risk appetite returning",
         transform=ax3.transAxes, fontsize=7, color="#888888", va="bottom")

style_panel(ax3)

# ---------------------------------------------------------------
# X-axis date labels — applied to all three panels.
#
# MonthLocator(interval=3) = one tick every 3 months (8 ticks total
# across 24 months — readable without crowding on a laptop).
# DateFormatter("%b '%y") = compact format: Apr '24, Jul '24, etc.
# Rotation=30 angled so labels don't overlap each other.
# ---------------------------------------------------------------
for ax in (ax1, ax2, ax3):
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right",
             fontsize=8, color=TEXT)

# ---------------------------------------------------------------
# Manual spacing — replaces tight_layout().
#
# top=0.94    leaves room between suptitle and the first panel title
# bottom=0.06 leaves room for the bottom x-axis date labels
# hspace=0.55 vertical gap between each pair of panels
#             (as a fraction of average panel height)
#
# This gives each panel title clear air above it and ensures x-axis
# date labels on one panel don't sit on top of the title below it.
# ---------------------------------------------------------------
fig.subplots_adjust(top=0.94, bottom=0.06, hspace=0.55)

plt.show()
print("Done.")
