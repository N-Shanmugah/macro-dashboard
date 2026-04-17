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
# Colour palette — edit here to change any colour globally.
# ---------------------------------------------------------------
BG    = "#0A0A0A"   # figure background (window border area)
PANEL = "#111111"   # plot area background
TEXT  = "#D0D0D0"   # labels, titles, tick values
GRID  = "#2A2A2A"   # faint gridlines
SPINE = "#333333"   # axis border lines

C_VIX    = "#FF4D4D"   # bright red
C_DXY    = "#4DA6FF"   # bright blue
C_MA     = "#A0C8FF"   # lighter blue — DXY 20-day MA
C_GOLD   = "#FFD700"   # gold / amber
C_EVENT  = "#555555"   # vertical event marker lines
C_ELABEL = "#999999"   # event label text

# ---------------------------------------------------------------
# Macro event markers.
# Each entry: (date string, two-line label shown on VIX panel)
# Vertical dotted lines will appear on all three panels so you
# can trace the cross-panel effect (DXY, Gold) at the same date.
# To add a new event: append ("YYYY-MM-DD", "Label\nline 2")
# Events outside the 24-month window are ignored automatically.
# ---------------------------------------------------------------
MACRO_EVENTS = [
    ("2024-08-05", "Yen carry\nunwind"),
    ("2024-11-05", "US Election\n(Trump)"),
    ("2025-04-02", "Liberation Day\n(tariffs)"),
]

# ---------------------------------------------------------------
# 24-month lookback window.
# ---------------------------------------------------------------
end_date   = pd.Timestamp.today()
start_date = end_date - pd.DateOffset(months=24)

print("Fetching data from Yahoo Finance...")

vix  = yf.download("^VIX",     start=start_date, end=end_date, auto_adjust=True, progress=False)["Close"].squeeze().dropna()
dxy  = yf.download("DX-Y.NYB", start=start_date, end=end_date, auto_adjust=True, progress=False)["Close"].squeeze().dropna()
gold = yf.download("GC=F",     start=start_date, end=end_date, auto_adjust=True, progress=False)["Close"].squeeze().dropna()

print(f"VIX:  {len(vix)} days  | Latest: {vix.iloc[-1]:.2f}")
print(f"DXY:  {len(dxy)} days  | Latest: {dxy.iloc[-1]:.2f}")
print(f"Gold: {len(gold)} days  | Latest: ${gold.iloc[-1]:,.0f}")
print("Building chart...")

# 20-day moving average on DXY to show trend direction.
dxy_ma20 = dxy.rolling(20).mean()

# ---------------------------------------------------------------
# Build figure — 3 stacked panels.
# figsize=(13, 13) suits a landscape laptop screen.
# ---------------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 13), sharex=False)
fig.patch.set_facecolor(BG)

# ---------------------------------------------------------------
# Dashboard header — split into two separate text elements so
# the main title and the date range line never sit on top of
# each other or crowd the first panel title below them.
#
# fig.text(x, y, ...) places text using figure-level coordinates
# where (0,0) = bottom-left and (1,1) = top-right of the window.
#
# ha="center" centres both lines on the horizontal midpoint.
# ---------------------------------------------------------------
fig.text(0.5, 0.977,
         "GLOBAL RISK SENTIMENT DASHBOARD",
         ha="center", fontsize=13, fontweight="bold", color=TEXT)

fig.text(0.5, 0.955,
         f"24-Month View  |  {start_date.strftime('%b %Y')} – {end_date.strftime('%b %Y')}",
         ha="center", fontsize=9, color="#888888")

# ---------------------------------------------------------------
# Helper: applies Bloomberg dark formatting to one panel.
# Called once per panel after all plotting is complete.
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
# Helper: draws event markers on a given panel.
#
# axvline() draws a vertical dotted line at the event date.
# ax.text() with get_xaxis_transform() lets us place the label
# using data-space x (the date) but axes-space y (0=bottom,
# 1=top), so the label always sits at the top of the panel
# regardless of the y-axis scale.
#
# Labels are shown only on the VIX panel (show_label=True).
# All three panels get the vertical line so you can trace
# DXY and Gold reactions to the same event.
# ---------------------------------------------------------------
def draw_events(ax, series, show_label=False):
    for date_str, label in MACRO_EVENTS:
        event_date = pd.Timestamp(date_str)
        if series.index[0] <= event_date <= series.index[-1]:
            ax.axvline(x=event_date, color=C_EVENT, linewidth=0.9,
                       linestyle=":", alpha=0.9, zorder=2)
            if show_label:
                ax.text(event_date, 0.97, label,
                        transform=ax.get_xaxis_transform(),
                        fontsize=6.5, color=C_ELABEL,
                        ha="center", va="top",
                        rotation=90, linespacing=1.3)

# ---------------------------------------------------------------
# PANEL 1: VIX — CBOE Volatility Index (investor fear gauge)
#
# Threshold lines:
#   20 = calm / elevated boundary (orange dashed)
#   30 = stress / fear (red dashed)
# Red shading above 30 = extreme fear zone.
# Event labels are shown here only.
# ---------------------------------------------------------------
ax1.plot(vix.index, vix.values, color=C_VIX, linewidth=1.6, label="VIX", zorder=3)

ax1.fill_between(vix.index, vix.values, 30,
                 where=(vix.values > 30),
                 color=C_VIX, alpha=0.18, label="Extreme fear (>30)")

ax1.axhline(y=20, color="#FFA500", linewidth=0.9, linestyle="--", alpha=0.75, label="Caution (20)")
ax1.axhline(y=30, color=C_VIX,    linewidth=0.9, linestyle="--", alpha=0.75, label="Stress (30)")

ax1.annotate(f" {vix.iloc[-1]:.1f}",
             xy=(vix.index[-1], vix.iloc[-1]),
             fontsize=9, color=C_VIX, va="center", fontweight="bold")

draw_events(ax1, vix, show_label=True)

ax1.set_title("VIX  —  Investor Fear Gauge", fontsize=10, fontweight="bold", pad=8)
ax1.set_ylabel("Level", fontsize=8, labelpad=6)
ax1.legend(loc="upper right", fontsize=7.5, facecolor=PANEL, edgecolor=SPINE, labelcolor=TEXT)
ax1.set_xlim(vix.index[0], vix.index[-1])

style_panel(ax1)

# ---------------------------------------------------------------
# PANEL 2: DXY — US Dollar Index
# Rising = risk-off (USD demand). Falling = risk-on.
# Dotted event lines only — no text labels to avoid clutter.
# ---------------------------------------------------------------
ax2.plot(dxy.index, dxy.values, color=C_DXY, linewidth=1.5, alpha=0.90, label="DXY", zorder=3)
ax2.plot(dxy_ma20.index, dxy_ma20.values, color=C_MA, linewidth=1.3,
         linestyle="--", label="20-Day MA", alpha=0.85)

ax2.annotate(f" {dxy.iloc[-1]:.2f}",
             xy=(dxy.index[-1], dxy.iloc[-1]),
             fontsize=9, color=C_DXY, va="center", fontweight="bold")

draw_events(ax2, dxy, show_label=False)

ax2.set_title("DXY  —  US Dollar Index", fontsize=10, fontweight="bold", pad=8)
ax2.set_ylabel("Level", fontsize=8, labelpad=6)
ax2.legend(loc="upper right", fontsize=7.5, facecolor=PANEL, edgecolor=SPINE, labelcolor=TEXT)
ax2.set_xlim(dxy.index[0], dxy.index[-1])

style_panel(ax2)

# ---------------------------------------------------------------
# PANEL 3: Gold — Safe Haven Demand (USD per troy ounce)
# Rising = risk-off / inflation / loss of confidence.
# Dotted event lines only — no text labels.
# ---------------------------------------------------------------
ax3.plot(gold.index, gold.values, color=C_GOLD, linewidth=1.8, label="Gold futures (USD/oz)", zorder=3)

ax3.fill_between(gold.index, gold.values, gold.values.min() * 0.995,
                 color=C_GOLD, alpha=0.10)

ax3.annotate(f" ${gold.iloc[-1]:,.0f}",
             xy=(gold.index[-1], gold.iloc[-1]),
             fontsize=9, color=C_GOLD, va="center", fontweight="bold")

draw_events(ax3, gold, show_label=False)

ax3.set_title("Gold  —  Safe Haven Demand", fontsize=10, fontweight="bold", pad=8)
ax3.set_ylabel("USD / oz", fontsize=8, labelpad=6)
ax3.legend(loc="upper right", fontsize=7.5, facecolor=PANEL, edgecolor=SPINE, labelcolor=TEXT)
ax3.set_xlim(gold.index[0], gold.index[-1])

style_panel(ax3)

# ---------------------------------------------------------------
# X-axis date labels — applied to all three panels.
# MonthLocator(interval=3) = one tick every 3 months.
# "%b '%y" = compact format e.g. "Apr '24".
# ---------------------------------------------------------------
for ax in (ax1, ax2, ax3):
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right",
             fontsize=8, color=TEXT)

# ---------------------------------------------------------------
# Spacing layout.
#
# top=0.92    — first panel starts well below the two header lines
#               (main title at y=0.977, date range at y=0.955)
# bottom=0.06 — room for the bottom x-axis date labels
# hspace=0.55 — vertical gap between panels so x-axis labels
#               on one panel never sit on the title of the next
# ---------------------------------------------------------------
fig.subplots_adjust(top=0.92, bottom=0.06, hspace=0.55)

plt.show()
print("Done.")
