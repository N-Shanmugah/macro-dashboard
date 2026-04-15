# FX Macro Dashboard

A Python-based macro rates dashboard that pulls live data from the FRED API and visualises key US interest rate indicators.

## What It Does

Fetches the following series from the Federal Reserve Economic Data (FRED) API:

| Series | Description |
|--------|-------------|
| FEDFUNDS | Federal Funds Effective Rate (monthly) |
| DGS2 | 2-Year Treasury Constant Maturity Rate |
| DGS5 | 5-Year Treasury Constant Maturity Rate |
| DGS10 | 10-Year Treasury Constant Maturity Rate |
| DGS30 | 30-Year Treasury Constant Maturity Rate |

Produces a 3-panel chart:
1. **Fed Funds Rate vs 10-Year Treasury Yield** — last 5 years
2. **Yield Curve Snapshot** — current rates across maturities (2Y, 5Y, 10Y, 30Y)
3. **2Y-10Y Spread** — with red shading to highlight inversion periods (recession signal)

## Setup

### 1. Clone the repo
```
git clone https://github.com/N-Shanmugah/macro-dashboard.git
cd macro-dashboard
```

### 2. Create and activate a virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```
pip install fredapi pandas matplotlib
```

### 4. Set your FRED API key

Get a free API key from [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)

Add it as a Windows environment variable named `FRED_API_KEY`:
- Search "Environment Variables" in the Start menu
- Under User variables, click New
- Variable name: `FRED_API_KEY`
- Variable value: your key

Restart VS Code after saving.

### 5. Run

```
python rates_chart.py
```

## Files

| File | Purpose |
|------|---------|
| `fred_test.py` | Verifies FRED API connection and prints latest rate values |
| `rates_chart.py` | Fetches data and renders the 3-panel chart |

## Requirements

- Python 3.10+
- `fredapi`
- `pandas`
- `matplotlib`

## Author

Built by [N-Shanmugah](https://github.com/N-Shanmugah) as part of a macro operations toolkit for family office investment management.
