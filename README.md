# Index Drop-Buy / Rally-Sell Simulator

A Streamlit app that backtests a simple rule on Indian stocks, indices, ETFs, mutual-fund proxies and world indices (data from yfinance): invest a fixed amount on every day the price falls by at least X%, and sell everything on a day it rises by at least Y%. The per-signal amount can step up every year.

```bash
pip install -r requirements.txt
streamlit run app.py
```

- `app.py`: UI and charts. `backtest.py`: the simulation (no Streamlit dependency).
- By default units are fractional (like a mutual fund / index NAV). Tick **Whole units only** in the sidebar to buy whole shares.
- "Max drawdown" is time-weighted (it measures the holdings, not money added by later buys).
- "CAGR (approx)" treats all invested money as if it had been invested for the whole period, so it understates the return of a strategy that invests gradually.

Tests: `pip install -r requirements-dev.txt && pytest` (offline; yfinance is faked).

Educational use only; not financial advice.
