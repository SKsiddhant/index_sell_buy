import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backtest import format_stat, run_backtest


def frame(prices, start="2023-12-27"):
    idx = pd.bdate_range(start, periods=len(prices))
    df = pd.DataFrame({"Close": [float(p) for p in prices]}, index=idx)
    df["Daily_Return"] = df["Close"].pct_change()
    return df


def run(prices, **kw):
    args = dict(buy_drop_pct=1.0, sell_rise_pct=2.0, invest_per_signal=1000, stepup_pct=0, years=1.0, whole_units=False)
    args.update(kw)
    return run_backtest(frame(prices), **args)


def test_buy_on_drop_then_sell_all_on_rally():
    r = run([100, 100, 98, 98, 101])          # -2% -> buy, +3.06% -> sell
    assert [t["Action"] for t in r["trades"]] == ["BUY", "SELL ALL"]
    buy, sell = r["trades"]
    assert buy["Units Bought"] == pytest.approx(1000 / 98)
    assert sell["Trade PnL (Rs)"] == pytest.approx(1000 / 98 * 101 - 1000, abs=0.01)
    assert r["units_held"] == 0 and r["net_pnl"] == pytest.approx(sell["Trade PnL (Rs)"], abs=0.01)


def test_fractional_units_buy_even_when_price_exceeds_budget():
    """Nifty 50 is the default instrument (~20,000+): whole-unit buying never traded at all."""
    prices = [25000, 25000, 24500, 24500]
    assert run(prices)["num_buys"] == 1
    assert run(prices, whole_units=True)["num_buys"] == 0


def test_whole_units_mode_spends_only_what_it_can():
    r = run([100, 100, 90], invest_per_signal=1050, whole_units=True)
    t = r["trades"][0]
    assert t["Units Bought"] == 11 and t["Amount Invested (Rs)"] == 990 and t["Leftover (Rs)"] == 60


def test_annual_stepup_applies_on_first_day_of_new_year():
    # Dec 29 2023 drop (year 1), Jan 2 2024 drop (year 2)
    df = frame([100, 100, 97, 94, 91], start="2023-12-27")
    r = run_backtest(df, 1.0, 50.0, 1000, 10, 1.0)
    amounts = [t["Budget (Rs)"] for t in r["trades"]]
    assert amounts[0] == 1000 and amounts[-1] == pytest.approx(1100)
    assert r["year_invest_map"][2023] == 1000 and r["year_invest_map"][2024] == pytest.approx(1100)


def test_year_map_has_no_30_year_cutoff():
    df = frame(np.linspace(100, 120, 5), start="2000-01-03")
    assert len(run_backtest(df, 1, 2, 1000, 10, 1.0)["year_invest_map"]) >= 1


def test_drawdown_is_zero_before_the_first_buy_and_negative_after_a_fall():
    r = run([100, 100, 100, 98, 90, 80], sell_rise_pct=50.0)
    dd = r["drawdown"]
    assert dd.iloc[0] == 0 and not dd.isna().any()
    assert r["max_dd"] < -10


def test_no_trades_gives_zero_metrics_not_errors():
    r = run([100, 100.1, 100.2, 100.3])
    assert r["trades"] == [] and r["net_pnl"] == 0 and r["cagr"] == 0 and r["max_dd"] == 0


def test_stats_are_formatted_by_unit_not_by_size():
    assert format_stat("Positive Days (%)", 52.3) == "52.30%"
    assert format_stat("Annualised Volatility (%)", 18.2) == "18.20%"
    assert format_stat("All-Time High (Rs)", 24000.5) == "Rs 24,000.50"
    assert format_stat("Start NAV / Price (Rs)", 0.5) == "Rs 0.50"
    assert format_stat("Total Trading Days", 1234) == "1,234"


def test_too_little_data_or_bad_years_raise_clear_errors():
    with pytest.raises(ValueError, match="at least 2"):
        run_backtest(frame([100]), 1.0, 2.0, 1000, 0, 1.0)
    with pytest.raises(ValueError, match="years"):
        run([100, 99, 98], years=0)
