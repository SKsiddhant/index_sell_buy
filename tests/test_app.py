import os
import sys
import types

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

HERE = os.path.join(os.path.dirname(__file__), "..")
APP = os.path.join(HERE, "app.py")


def make_prices(n=400):
    rng = np.random.default_rng(1)
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    close = 20000 * np.cumprod(1 + rng.normal(0.0004, 0.012, n))
    return pd.DataFrame({"Close": close, "Open": close, "High": close, "Low": close, "Volume": 1}, index=idx)


@pytest.fixture(autouse=True)
def fake_yfinance(monkeypatch):
    import streamlit as st
    st.cache_data.clear()  # fetch_data is cached in-process; every test must hit the (fake) download
    calls = []

    def download(ticker, start=None, end=None, **kw):
        calls.append((ticker, start, end))
        df = make_prices()
        df.columns = pd.MultiIndex.from_product([df.columns, [ticker]])  # yfinance returns MultiIndex columns
        return df

    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=download))
    monkeypatch.syspath_prepend(HERE)
    return calls


def run_app(custom=""):
    at = AppTest.from_file(APP, default_timeout=60).run()
    if custom:
        at.sidebar.text_input[0].set_value(custom)
    at.sidebar.button[0].click().run()
    return at


def test_default_run_renders_with_trades_on_a_high_priced_index(fake_yfinance):
    at = run_app()
    assert not at.exception, at.exception
    # Positive-days must be shown as a percentage, not as rupees
    stats = [df.value for df in at.dataframe if "Metric" in df.value.columns][0]
    assert stats.loc[stats["Metric"] == "Positive Days (%)", "Value"].iloc[0].endswith("%")
    assert any(m.label == "🛒 Buy Signals" and int(m.value) > 0 for m in at.metric)


def test_end_date_is_included_in_the_download(fake_yfinance):
    run_app()
    _, _, end = fake_yfinance[0]
    assert end > str(pd.Timestamp.today().date())


def test_custom_ticker_with_spaces_is_rejected_before_downloading(fake_yfinance):
    at = run_app("AAPL MSFT")
    assert any("single ticker" in e.value for e in at.sidebar.error)
    assert fake_yfinance == []


def test_start_after_end_is_an_error_not_a_crash(fake_yfinance):
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.date_input[0].set_value(pd.Timestamp.today().date())
    at.sidebar.date_input[1].set_value(pd.Timestamp.today().date() - pd.Timedelta(days=5))
    at.sidebar.button[0].click().run()
    assert not at.exception and any("before the end date" in e.value for e in at.sidebar.error)
