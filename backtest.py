"""Drop-buy / rally-sell backtest, kept free of Streamlit so it can be tested."""
import numpy as np
import pandas as pd


def run_backtest(df, buy_drop_pct, sell_rise_pct, invest_per_signal, stepup_pct, years, whole_units=False):
    """df: DataFrame indexed by date with a float 'Close' column and a 'Daily_Return' column.

    Each day: if the daily return <= -buy_drop_pct, invest the current per-signal amount; if it is
    >= +sell_rise_pct and units are held, sell everything. The per-signal amount grows by stepup_pct
    on the first trading day of each new year.

    whole_units=False buys fractional units (what the app's description promises, like a mutual fund
    or an index NAV). Whole units only were bought before, so on an instrument priced above the
    per-signal amount (the default, Nifty 50, trades at ~Rs 20,000+) no buy ever happened.
    """
    units_held = 0.0
    buy_cost_basis = []  # (units, price)
    trades, port_vals = [], []
    total_invested = total_withdrawn = realised_pnl = 0.0

    buy_thr = -buy_drop_pct / 100.0
    sell_thr = sell_rise_pct / 100.0

    current_year = df.index[1].year
    current_invest_amt = float(invest_per_signal)

    # year -> Rs per signal (for the schedule tables); no 30-year cut-off
    first_year, last_year = df.index[0].year, df.index[-1].year
    year_invest_map, amt = {}, float(invest_per_signal)
    for yr in range(df.index[1].year, last_year + 1):
        year_invest_map[yr] = round(amt, 2)
        amt *= 1 + stepup_pct / 100.0
    year_invest_map.setdefault(first_year, float(invest_per_signal))

    for i in range(1, len(df)):
        today = df.index[i]
        price = float(df["Close"].iloc[i])
        ret = float(df["Daily_Return"].iloc[i])
        if np.isnan(ret):
            continue

        # Value of what we already hold at today's price, before today's trade: used for the time-weighted
        # drawdown below (new money added by a buy must not hide a loss on the existing position)
        pre_trade_value = units_held * price + total_withdrawn

        if today.year != current_year:
            current_year = today.year
            current_invest_amt *= 1 + stepup_pct / 100.0

        if ret <= buy_thr:
            invest_amt = current_invest_amt
            units_bought = float(int(invest_amt // price)) if whole_units else invest_amt / price
            if units_bought > 0:
                actual_spent = units_bought * price
                units_held += units_bought
                total_invested += actual_spent
                buy_cost_basis.append((units_bought, price))
                cost = sum(u * p for u, p in buy_cost_basis)
                avg_cost = cost / sum(u for u, _ in buy_cost_basis)
                trades.append({
                    "Date": today, "Action": "BUY", "NAV / Price (Rs)": round(price, 4),
                    "Amount Invested (Rs)": round(actual_spent, 2), "Budget (Rs)": round(invest_amt, 2),
                    "Leftover (Rs)": round(invest_amt - actual_spent, 2), "Units Bought": units_bought,
                    "Total Units Held": round(units_held, 4), "Avg Cost (Rs)": round(avg_cost, 4),
                    "Daily Return (%)": round(ret * 100, 3), "Cumul Invested (Rs)": round(total_invested, 2),
                    "Trade PnL (Rs)": float("nan"),
                })
        elif ret >= sell_thr and units_held > 0:
            proceeds = units_held * price
            cost_basis = sum(u * p for u, p in buy_cost_basis)
            avg_cost = cost_basis / sum(u for u, _ in buy_cost_basis)
            pnl = proceeds - cost_basis
            total_withdrawn += proceeds
            realised_pnl += pnl
            trades.append({
                "Date": today, "Action": "SELL ALL", "NAV / Price (Rs)": round(price, 4),
                "Amount Invested (Rs)": float("nan"), "Units Bought": float("nan"),
                "Total Units Held": 0.0, "Avg Cost (Rs)": round(avg_cost, 4),
                "Daily Return (%)": round(ret * 100, 3), "Cumul Invested (Rs)": round(total_invested, 2),
                "Trade PnL (Rs)": round(pnl, 2),
            })
            units_held = 0.0
            buy_cost_basis = []

        port_vals.append({
            "Date": today, "Price": price, "Units_Held": units_held,
            "Portfolio_Value": units_held * price + total_withdrawn, "Total_Invested": total_invested,
            "Pre_Trade_Value": pre_trade_value,
        })

    pv_df = pd.DataFrame(port_vals).set_index("Date")
    final_price = float(df["Close"].iloc[-1])
    open_cost = sum(u * p for u, p in buy_cost_basis)
    unrealised_value = units_held * final_price
    unrealised_pnl = unrealised_value - open_cost if units_held > 0 else 0.0
    total_current_value = total_withdrawn + unrealised_value
    net_pnl = total_current_value - total_invested
    total_return_pct = net_pnl / total_invested * 100 if total_invested > 0 else 0.0
    avg_cost_held = open_cost / sum(u for u, _ in buy_cost_basis) if buy_cost_basis else 0.0

    # Time-weighted drawdown. Portfolio_Value includes every new buy, so a drawdown computed on it hid
    # losses whenever the strategy kept buying the dip (value kept making new highs while prices fell).
    # Here each day's return is the move of the existing holdings only; before the first buy it is 0.
    prev_value = pv_df["Portfolio_Value"].shift(1)
    daily = (pv_df["Pre_Trade_Value"] / prev_value - 1).where(prev_value > 0, 0.0).fillna(0.0)
    equity = (1 + daily).cumprod()
    drawdown = (equity / equity.cummax() - 1) * 100
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0

    cagr = ((total_current_value / total_invested) ** (1 / years) - 1) * 100 if total_invested > 0 else 0.0

    return {
        "units_held": units_held, "trades": trades, "pv_df": pv_df,
        "total_invested": total_invested, "total_withdrawn": total_withdrawn, "realised_pnl": realised_pnl,
        "final_price": final_price, "unrealised_value": unrealised_value, "unrealised_pnl": unrealised_pnl,
        "total_current_value": total_current_value, "net_pnl": net_pnl, "total_return_pct": total_return_pct,
        "avg_cost_held": avg_cost_held, "num_buys": sum(t["Action"] == "BUY" for t in trades),
        "num_sells": sum(t["Action"] == "SELL ALL" for t in trades), "drawdown": drawdown, "max_dd": max_dd,
        "cagr": cagr, "year_invest_map": year_invest_map,
    }


def format_stat(metric, value):
    """The statistics table formats every value by its own unit. The old code guessed from the size
    (> 1 means rupees), so 'Positive Days (%)' = 52.3 was shown as 'Rs 52.30'."""
    if metric.endswith("(Rs)"):
        return f"Rs {value:,.2f}"
    if metric.endswith("(%)"):
        return f"{value:.2f}%"
    return f"{int(value):,}"
