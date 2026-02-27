import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

st.set_page_config(
    page_title="Index Drop-Buy / Rally-Sell Simulator",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.5rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

INDICES = {
    "S&P 500 (USA)":             "^GSPC",
    "NASDAQ 100 (USA)":          "^NDX",
    "Dow Jones (USA)":           "^DJI",
    "Russell 2000 (USA)":        "^RUT",
    "TSX Composite (Canada)":    "^GSPTSE",
    "Bovespa (Brazil)":          "^BVSP",
    "FTSE 100 (UK)":             "^FTSE",
    "DAX (Germany)":             "^GDAXI",
    "CAC 40 (France)":           "^FCHI",
    "EURO STOXX 50":             "^STOXX50E",
    "AEX (Netherlands)":         "^AEX",
    "SMI (Switzerland)":         "^SSMI",
    "IBEX 35 (Spain)":           "^IBEX",
    "Nikkei 225 (Japan)":        "^N225",
    "Hang Seng (Hong Kong)":     "^HSI",
    "CSI 300 (China)":           "000300.SS",
    "Sensex (India)":            "^BSESN",
    "Nifty 50 (India)":          "^NSEI",
    "KOSPI (South Korea)":       "^KS11",
    "ASX 200 (Australia)":       "^AXJO",
    "Straits Times (Singapore)": "^STI",
    "TWSE (Taiwan)":             "^TWII",
    "Tadawul (Saudi Arabia)":    "^TASI.SR",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("Strategy Parameters")

selected_name = st.sidebar.selectbox("Select Index", list(INDICES.keys()))
ticker_symbol = INDICES[selected_name]

custom_ticker = st.sidebar.text_input("Custom ticker (overrides above):", placeholder="e.g. ^N225")
if custom_ticker.strip():
    ticker_symbol = custom_ticker.strip().upper()
    selected_name = ticker_symbol

st.sidebar.markdown("---")

buy_drop_pct  = st.sidebar.slider("BUY when daily drop >= (%)",  0.1, 10.0, 1.0, 0.1)
sell_rise_pct = st.sidebar.slider("SELL ALL when daily rise >= (%)", 0.1, 15.0, 2.0, 0.1)
lots_per_buy  = st.sidebar.number_input("Units bought per trigger", 1, 100, 1)
initial_capital = st.sidebar.number_input("Starting Capital ($)", 1000, 10_000_000, 100_000, 1000)

st.sidebar.markdown("---")
col_s, col_e = st.sidebar.columns(2)
start_date = col_s.date_input("Start", value=date.today() - timedelta(days=365 * 3))
end_date   = col_e.date_input("End",   value=date.today())

run_btn = st.sidebar.button("Run Simulation", use_container_width=True, type="primary")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("World Index — Drop & Buy / Rally & Sell Simulator")
st.caption("Accumulate on dips, sell everything on rallies.")

if not run_btn:
    st.info("Set your parameters in the sidebar and click Run Simulation.")
    st.markdown("""
### How It Works

Each trading day the app checks the daily return: `(Close_today / Close_yesterday) - 1`

- If return is **<= −buy_drop %** → **BUY** X lots at today's close (keeps stacking)
- If return is **>= +sell_rise %** AND you hold positions → **SELL ALL** at today's close

Open positions are marked-to-market for a live portfolio value every day.
A Buy-and-Hold benchmark is included for comparison.
    """)
    st.stop()

# ── Fetch Data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_data(ticker, start, end):
    return yf.download(ticker, start=str(start), end=str(end),
                       progress=False, auto_adjust=True)

with st.spinner("Downloading data..."):
    raw = fetch_data(ticker_symbol, start_date, end_date)

if raw is None or raw.empty:
    st.error(f"No data for '{ticker_symbol}'. Check ticker and date range.")
    st.stop()

if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.get_level_values(0)

if "Close" not in raw.columns:
    st.error("Could not find 'Close' column. Try a different ticker.")
    st.stop()

df = raw[["Close"]].copy()
df.index = pd.to_datetime(df.index)
df["Close"] = df["Close"].astype(float)
df = df.dropna()
df["Daily_Return"] = df["Close"].pct_change()

if len(df) < 5:
    st.error("Not enough data. Try a wider date range.")
    st.stop()

# ── Backtest ───────────────────────────────────────────────────────────────────
cash       = float(initial_capital)
lots_held  = 0
buy_prices = []
trades     = []
port_vals  = []

buy_thr  = -buy_drop_pct  / 100.0
sell_thr =  sell_rise_pct / 100.0

for i in range(1, len(df)):
    today = df.index[i]
    price = float(df["Close"].iloc[i])
    ret   = float(df["Daily_Return"].iloc[i])

    if np.isnan(ret):
        continue

    if ret <= buy_thr:
        cost = price * lots_per_buy
        if cash >= cost:
            cash -= cost
            lots_held += lots_per_buy
            buy_prices.extend([price] * lots_per_buy)
            trades.append({
                "Date":             today,
                "Action":           "BUY",
                "Price":            round(price, 4),
                "Lots":             lots_per_buy,
                "Daily Return (%)": round(ret * 100, 3),
                "Cash After":       round(cash, 2),
                "Avg Buy Price":    float("nan"),
                "Trade P&L":        float("nan"),
            })

    elif ret >= sell_thr and lots_held > 0:
        proceeds  = price * lots_held
        avg_buy   = float(np.mean(buy_prices))
        pnl       = (price - avg_buy) * lots_held
        cash     += proceeds
        trades.append({
            "Date":             today,
            "Action":           "SELL ALL",
            "Price":            round(price, 4),
            "Lots":             lots_held,
            "Daily Return (%)": round(ret * 100, 3),
            "Cash After":       round(cash, 2),
            "Avg Buy Price":    round(avg_buy, 4),
            "Trade P&L":        round(pnl, 2),
        })
        lots_held  = 0
        buy_prices = []

    port_vals.append({
        "Date":            today,
        "Price":           price,
        "Cash":            cash,
        "Lots":            lots_held,
        "Portfolio_Value": cash + lots_held * price,
    })

pv_df = pd.DataFrame(port_vals).set_index("Date")

final_price  = float(df["Close"].iloc[-1])
open_pnl     = (final_price - float(np.mean(buy_prices))) * lots_held if lots_held > 0 else 0.0
final_value  = float(pv_df["Portfolio_Value"].iloc[-1]) if not pv_df.empty else initial_capital

first_price      = float(df["Close"].iloc[1])
bh_values        = initial_capital * (df["Close"].iloc[1:] / first_price)
total_ret_pct    = (final_value - initial_capital) / initial_capital * 100
bh_ret_pct       = (float(bh_values.iloc[-1]) - initial_capital) / initial_capital * 100
num_buys         = sum(1 for t in trades if t["Action"] == "BUY")
num_sells        = sum(1 for t in trades if t["Action"] == "SELL ALL")
total_trade_pnl  = float(np.nansum([t.get("Trade P&L", 0) or 0 for t in trades]))

roll_max = pv_df["Portfolio_Value"].cummax()
drawdown = (pv_df["Portfolio_Value"] - roll_max) / roll_max * 100
max_dd   = float(drawdown.min())

# ── KPIs ───────────────────────────────────────────────────────────────────────
st.markdown("## " + selected_name + "  `" + ticker_symbol + "`")
st.caption(
    str(start_date) + " to " + str(end_date) +
    "  |  Buy >= -" + str(buy_drop_pct) + "%" +
    "  |  Sell >= +" + str(sell_rise_pct) + "%" +
    "  |  " + str(lots_per_buy) + " lot(s)/buy"
)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Final Value",     "$" + f"{final_value:,.0f}",  f"{total_ret_pct:+.2f}%")
c2.metric("Strategy Return", f"{total_ret_pct:.2f}%",      "B&H: " + f"{bh_ret_pct:.2f}%")
c3.metric("Buy & Hold",      f"{bh_ret_pct:.2f}%")
c4.metric("Buy Signals",     num_buys)
c5.metric("Sell Signals",    num_sells)
c6.metric("Max Drawdown",    f"{max_dd:.2f}%")

c7, c8, c9 = st.columns(3)
c7.metric("Realised P&L",    "$" + f"{total_trade_pnl:,.2f}")
c8.metric("Open Lots",       str(lots_held) + "  ($" + f"{open_pnl:+,.2f}" + ")")
c9.metric("Cash Remaining",  "$" + f"{cash:,.2f}")

# ── Main Chart ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Equity Curve & Trade Signals")

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    row_heights=[0.50, 0.30, 0.20],
    vertical_spacing=0.04,
    subplot_titles=("Portfolio Value vs Buy & Hold", "Index Price + Signals", "Daily Return (%)"),
)

fig.add_trace(go.Scatter(x=pv_df.index, y=pv_df["Portfolio_Value"],
    name="Strategy", line=dict(color="#60a5fa", width=2)), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index[1:], y=bh_values,
    name="Buy & Hold", line=dict(color="#f59e0b", width=2, dash="dash")), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df["Close"],
    name="Index", line=dict(color="#a78bfa", width=1.5)), row=2, col=1)

buy_trades  = [t for t in trades if t["Action"] == "BUY"]
sell_trades = [t for t in trades if t["Action"] == "SELL ALL"]

if buy_trades:
    fig.add_trace(go.Scatter(
        x=[t["Date"] for t in buy_trades],
        y=[t["Price"] for t in buy_trades],
        mode="markers", name="BUY",
        marker=dict(symbol="triangle-up", color="#4ade80", size=10,
                    line=dict(width=1, color="#166534")),
    ), row=2, col=1)

if sell_trades:
    fig.add_trace(go.Scatter(
        x=[t["Date"] for t in sell_trades],
        y=[t["Price"] for t in sell_trades],
        mode="markers", name="SELL ALL",
        marker=dict(symbol="triangle-down", color="#f87171", size=12,
                    line=dict(width=1, color="#991b1b")),
    ), row=2, col=1)

ret_series = df["Daily_Return"].iloc[1:] * 100
bar_colors = ["#4ade80" if v >= 0 else "#f87171" for v in ret_series]
fig.add_trace(go.Bar(x=df.index[1:], y=ret_series,
    marker_color=bar_colors, name="Daily Ret%", showlegend=False), row=3, col=1)

fig.add_hline(y=-buy_drop_pct,  line=dict(color="#4ade80", dash="dot", width=1), row=3, col=1)
fig.add_hline(y=sell_rise_pct,  line=dict(color="#f87171", dash="dot", width=1), row=3, col=1)

fig.update_layout(
    height=750, template="plotly_dark",
    plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    margin=dict(l=50, r=20, t=50, b=20),
    hovermode="x unified",
)
fig.update_yaxes(gridcolor="#1e293b")
fig.update_xaxes(gridcolor="#1e293b")
st.plotly_chart(fig, use_container_width=True)

# ── Drawdown ───────────────────────────────────────────────────────────────────
st.subheader("Drawdown")
dd_fig = go.Figure(go.Scatter(
    x=drawdown.index, y=drawdown,
    fill="tozeroy", fillcolor="rgba(248,113,113,0.15)",
    line=dict(color="#f87171", width=1.5),
))
dd_fig.update_layout(
    height=200, template="plotly_dark",
    plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
    margin=dict(l=50, r=20, t=10, b=20),
    yaxis_title="Drawdown (%)", showlegend=False,
)
dd_fig.update_yaxes(gridcolor="#1e293b")
dd_fig.update_xaxes(gridcolor="#1e293b")
st.plotly_chart(dd_fig, use_container_width=True)

# ── Trade Log ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Trade Log")

if trades:
    trade_df = pd.DataFrame(trades)
    trade_df["Date"] = pd.to_datetime(trade_df["Date"]).dt.date

    def highlight_action(val):
        if val == "BUY":
            return "color: #4ade80; font-weight: bold;"
        elif val == "SELL ALL":
            return "color: #f87171; font-weight: bold;"
        return ""

    def highlight_pnl(val):
        if pd.isna(val):
            return ""
        try:
            return "color: #4ade80;" if float(val) >= 0 else "color: #f87171;"
        except Exception:
            return ""

    fmt = {
        "Price":            "{:.4f}",
        "Cash After":       "{:,.2f}",
        "Daily Return (%)": "{:+.3f}",
        "Avg Buy Price":    "{:.4f}",
        "Trade P&L":        "{:+,.2f}",
    }
    styled = (
        trade_df.style
        .applymap(highlight_action, subset=["Action"])
        .applymap(highlight_pnl, subset=["Trade P&L"])
        .format(fmt, na_rep="—")
    )
    st.dataframe(styled, use_container_width=True, height=350)
    csv_data = trade_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Trade Log (CSV)", csv_data, "trade_log.csv", "text/csv")
else:
    st.info("No trades triggered. Try adjusting the drop / rise thresholds.")

# ── Monthly Heatmap ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Monthly Portfolio Return Heatmap")

if not pv_df.empty:
    pv_m   = pv_df["Portfolio_Value"].resample("ME").last()
    m_ret  = pv_m.pct_change().dropna() * 100
    m_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    pivot = pd.DataFrame({
        "Return": m_ret.values,
        "Year":   m_ret.index.year,
        "Month":  m_ret.index.month,
    }).pivot(index="Year", columns="Month", values="Return")
    pivot.columns = [m_names[m - 1] for m in pivot.columns]

    z_data = pivot.values.tolist()
    txt    = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in pivot.values]

    hm = go.Figure(go.Heatmap(
        z=z_data, x=pivot.columns.tolist(),
        y=[str(y) for y in pivot.index.tolist()],
        text=txt, texttemplate="%{text}",
        colorscale="RdYlGn", zmid=0,
        colorbar=dict(title="Return %"),
    ))
    hm.update_layout(
        height=max(220, 55 * len(pivot)),
        template="plotly_dark",
        plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
        margin=dict(l=60, r=20, t=20, b=40),
    )
    st.plotly_chart(hm, use_container_width=True)

st.markdown("---")
st.caption("Backtesting simulator for educational purposes only. Not financial advice.")
