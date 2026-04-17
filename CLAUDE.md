# CLAUDE.md — FX Macro Dashboard

## What This Project Is

A Python-based macro monitoring dashboard built for investment operations and family office use.
Currently focused on US interest rates via the FRED API. Intended to grow into a multi-panel
dashboard covering rates, FX, credit, and equity macro signals — with a simple, clean output
suitable for briefing materials or daily monitoring.

This is a learning-by-building project. The code should be readable and well-commented.
Every function should be explainable in plain English.

---

## Current State (as of April 2026)

### Files
| File | Purpose |
|------|---------|
| `fred_test.py` | API connection test — prints latest values for DGS10 and FEDFUNDS |
| `rates_chart.py` | Rates dashboard — Fed Funds vs 10Y, yield curve snapshot, 2Y-10Y spread |
| `risk_sentiment.py` | Global risk sentiment — VIX, DXY, Gold (24-month view, Yahoo Finance) |

### What `rates_chart.py` Produces
1. **Fed Funds Rate vs 10Y Treasury Yield** — last 5 years overlay
2. **Yield Curve Snapshot** — current rates at 2Y, 5Y, 10Y, 30Y
3. **2Y-10Y Spread** — with red shading on inversion periods

### What `risk_sentiment.py` Produces
1. **VIX** — fear gauge with zone shading above 30, reference lines at 20 and 30
2. **DXY** — US Dollar Index with 20-day moving average
3. **Gold** — safe haven demand in USD/oz with amber fill

Style: Bloomberg dark (black background, bright line colours, interpretation keys inside each panel)

### Data Sources
- FRED API (`fredapi`) — rates data; key stored as `FRED_API_KEY` environment variable
- Yahoo Finance (`yfinance`) — VIX (`^VIX`), DXY (`DX-Y.NYB`), Gold futures (`GC=F`); no key required
- Series: `FEDFUNDS`, `DGS2`, `DGS5`, `DGS10`, `DGS30`

---

## Planned Expansion (to be built incrementally)

The dashboard is intended to grow across multiple sessions. Planned additions include:

### Rates (in progress)
- [ ] Add recession band shading (NBER recession dates from FRED: `USREC`)
- [ ] Extend to include real yields (TIPS: `DFII10`)
- [ ] Add Fed Funds futures or market-implied rate path (if data available)

### FX Panel
- [x] USD Index (DXY) — built in `risk_sentiment.py`
- [ ] Key pairs: EUR/USD, USD/JPY, USD/SGD
- [ ] Source: Yahoo Finance (`yfinance`) or FRED FX series

### Credit / Risk Panel
- [ ] Investment grade and high yield credit spreads (FRED: `BAMLC0A0CM`, `BAMLH0A0HYM2`)
- [x] VIX (equity volatility) — built in `risk_sentiment.py`
- [ ] Could combine into a single "risk-off signal" composite

### Equity Macro
- [ ] S&P 500 price trend (via `yfinance`)
- [ ] PE ratio or earnings yield (if data available)

### Output / UX
- [ ] Option to save chart as PNG with datestamp
- [ ] Consider a simple Tkinter window wrapper for non-terminal use
- [ ] Potential: single entry point (`dashboard.py`) that runs all panels

---

## Architecture Principles

- One script per data domain (rates, FX, credit) until there is a reason to consolidate
- No web server, no database — flat Python scripts outputting matplotlib charts
- All data pulled live at runtime — no caching layer yet
- Virtual environment (`venv/`) always — never install globally
- API keys via environment variables only — never hardcoded

---

## Environment

- OS: Windows 11
- Shell: VS Code integrated terminal (bash)
- Python: 3.10+
- Virtual env: `venv/` in project root
- Activate: `venv/Scripts/activate` (Windows)
- Key dependencies: `fredapi`, `pandas`, `matplotlib`, `yfinance`

---

## Coding Conventions

- Comments above every function explaining what it does in plain English
- Explain non-obvious pandas/matplotlib operations inline
- Use descriptive variable names — `fedfunds_5y` not `ff`
- Print progress messages when fetching data so the user knows the script is running
- Guard against missing API keys at the top of every script
- Prefer explicit filtering (e.g. `series[series.index >= cutoff]`) over implicit slicing

## Chart Style — Bloomberg Dark

All new charts follow this standard:
- Background: `#0A0A0A` (figure), `#111111` (panel)
- Text / ticks: `#D0D0D0`
- Grid: `#2A2A2A`, spines: `#333333`
- Top and right spines removed for clean look
- Interpretation keys placed as small grey text *inside* the bottom of each panel (not in the title)
- `fig.subplots_adjust(top=0.94, bottom=0.06, hspace=0.55)` — do not use `tight_layout()`
- X-axis date format: `%b '%y` (e.g. `Apr '24`) — compact for laptop screens
- Colour palette defined at the top of each script as named constants (e.g. `C_VIX`, `C_DXY`)

---

## Git Workflow

Follow the step-by-step workflow defined in the global CLAUDE.md:
Stage → Commit → Push as separate confirmed steps.
Never combine without explicit approval.

Remote: `https://github.com/N-Shanmugah/macro-dashboard`
Branch: `master`
