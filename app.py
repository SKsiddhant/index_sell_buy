import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

st.set_page_config(
    page_title="Indian Market & World Index Trading Simulator",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.4rem; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 0.8rem; }
.category-header { color: #f59e0b; font-weight: 700; font-size: 0.8rem;
                   text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  MASTER TICKER DICTIONARY  (grouped by category)
# ══════════════════════════════════════════════════════════════════════
CATEGORIES = {

    # ── INDIAN BROAD INDICES ──────────────────────────────────────────
    "🇮🇳 Indian Broad Indices": {
        "Nifty 50":                    "^NSEI",
        "BSE Sensex":                  "^BSESN",
        "Nifty Next 50":               "^NSMIDCP",
        "Nifty 100":                   "^CNX100",
        "Nifty 200":                   "^CNX200",
        "Nifty 500":                   "^CNX500",
        "Nifty Midcap 50":             "^NSEMDCP50",
        "Nifty Midcap 100":            "^CNXMidcap",
        "Nifty Smallcap 100":          "^CNXSC",
        "Nifty Smallcap 250":          "NIFTYSMALLCAP250.NS",
        "BSE MidCap":                  "BSE-MIDCAP.BO",
        "BSE SmallCap":                "BSE-SMLCAP.BO",
        "Nifty Microcap 250":          "NIFTYMICROCAP250.NS",
        "Nifty LargeMidcap 250":       "NIFTYLARGEMID250.NS",
    },

    # ── INDIAN SECTORAL INDICES ───────────────────────────────────────
    "📊 Indian Sectoral Indices": {
        "Nifty Bank":                  "^NSEBANK",
        "Nifty IT":                    "^CNXIT",
        "Nifty FMCG":                  "^CNXFMCG",
        "Nifty Auto":                  "^CNXAUTO",
        "Nifty Pharma":                "^CNXPHARMA",
        "Nifty Metal":                 "^CNXMETAL",
        "Nifty Realty":                "^CNXREALTY",
        "Nifty Energy":                "^CNXENERGY",
        "Nifty Infrastructure":        "^CNXINFRA",
        "Nifty Media":                 "^CNXMEDIA",
        "Nifty PSU Bank":              "^CNXPSUBANK",
        "Nifty Private Bank":          "NIFTYPVTBANK.NS",
        "Nifty Financial Services":    "NIFTYFINSERVICE.NS",
        "Nifty Healthcare":            "NIFTYHEALTHCARE.NS",
        "Nifty Consumer Durables":     "NIFTYCONSDUR.NS",
        "Nifty Oil & Gas":             "NIFTYOILGAS.NS",
        "Nifty Commodities":           "^CNXCMDT",
        "Nifty India Defence":         "NIFTYINDIADEFENCE.NS",
        "Nifty India Manufacturing":   "NIFTYINDIAMANUFACTURING.NS",
        "Nifty PSE":                   "^CNXPSE",
        "Nifty MNC":                   "^CNXMNC",
        "Nifty Service Sector":        "^CNXSERVICE",
        "BSE Bankex":                  "BSE-BANKEX.BO",
        "BSE Capital Goods":           "BSE-CG.BO",
        "BSE Healthcare":              "BSE-HC.BO",
        "BSE IT":                      "BSE-IT.BO",
        "BSE FMCG":                    "BSE-FMCG.BO",
        "BSE Auto":                    "BSE-AUTO.BO",
        "BSE Metal":                   "BSE-METAL.BO",
        "BSE Oil & Gas":               "BSE-OILGAS.BO",
        "BSE Realty":                  "BSE-REALTY.BO",
        "BSE Power":                   "BSE-POWER.BO",
        "BSE Telecom":                 "BSE-TECK.BO",
        "BSE Consumer Discretionary":  "BSE-CD.BO",
    },

    # ── NIFTY 50 STOCKS ───────────────────────────────────────────────
    "💰 Nifty 50 Stocks": {
        "Reliance Industries":         "RELIANCE.NS",
        "TCS":                         "TCS.NS",
        "HDFC Bank":                   "HDFCBANK.NS",
        "Infosys":                     "INFY.NS",
        "ICICI Bank":                  "ICICIBANK.NS",
        "Hindustan Unilever":          "HINDUNILVR.NS",
        "ITC":                         "ITC.NS",
        "State Bank of India":         "SBIN.NS",
        "Bharti Airtel":               "BHARTIARTL.NS",
        "Kotak Mahindra Bank":         "KOTAKBANK.NS",
        "Larsen & Toubro":             "LT.NS",
        "Bajaj Finance":               "BAJFINANCE.NS",
        "HCL Technologies":            "HCLTECH.NS",
        "Asian Paints":                "ASIANPAINT.NS",
        "Axis Bank":                   "AXISBANK.NS",
        "Maruti Suzuki":               "MARUTI.NS",
        "Sun Pharma":                  "SUNPHARMA.NS",
        "Titan Company":               "TITAN.NS",
        "Wipro":                       "WIPRO.NS",
        "Adani Ports":                 "ADANIPORTS.NS",
        "UltraTech Cement":            "ULTRACEMCO.NS",
        "Nestle India":                "NESTLEIND.NS",
        "Tech Mahindra":               "TECHM.NS",
        "NTPC":                        "NTPC.NS",
        "Power Grid Corp":             "POWERGRID.NS",
        "IndusInd Bank":               "INDUSINDBK.NS",
        "M&M":                         "M&M.NS",
        "Bajaj Finserv":               "BAJAJFINSV.NS",
        "JSW Steel":                   "JSWSTEEL.NS",
        "Tata Motors":                 "TATAMOTORS.NS",
        "Grasim Industries":           "GRASIM.NS",
        "Dr Reddys":                   "DRREDDY.NS",
        "Adani Enterprises":           "ADANIENT.NS",
        "Cipla":                       "CIPLA.NS",
        "Coal India":                  "COALINDIA.NS",
        "Eicher Motors":               "EICHERMOT.NS",
        "Hindalco":                    "HINDALCO.NS",
        "ONGC":                        "ONGC.NS",
        "Tata Steel":                  "TATASTEEL.NS",
        "Hero MotoCorp":               "HEROMOTOCO.NS",
        "Divi's Lab":                  "DIVISLAB.NS",
        "SBI Life Insurance":          "SBILIFE.NS",
        "HDFC Life":                   "HDFCLIFE.NS",
        "Tata Consumer":               "TATACONSUM.NS",
        "Apollo Hospitals":            "APOLLOHOSP.NS",
        "Britannia":                   "BRITANNIA.NS",
        "BPCL":                        "BPCL.NS",
        "Shriram Finance":             "SHRIRAMFIN.NS",
        "BEL":                         "BEL.NS",
        "Trent":                       "TRENT.NS",
    },

    # ── POPULAR MID CAP STOCKS ────────────────────────────────────────
    "📈 Popular Mid Cap Stocks": {
        "Avenue Supermarts (DMart)":   "DMART.NS",
        "Zomato":                      "ZOMATO.NS",
        "Paytm":                       "PAYTM.NS",
        "Nykaa":                       "FSN.NS",
        "PolicyBazaar":                "POLICYBZR.NS",
        "Delhivery":                   "DELHIVERY.NS",
        "Mamaearth":                   "HONASA.NS",
        "IRCTC":                       "IRCTC.NS",
        "Havells India":               "HAVELLS.NS",
        "Godrej Consumer":             "GODREJCP.NS",
        "Pidilite":                    "PIDILITIND.NS",
        "Torrent Pharma":              "TORNTPHARM.NS",
        "Lupin":                       "LUPIN.NS",
        "Muthoot Finance":             "MUTHOOTFIN.NS",
        "Bajaj Auto":                  "BAJAJ-AUTO.NS",
        "Bosch":                       "BOSCHLTD.NS",
        "Siemens":                     "SIEMENS.NS",
        "ABB India":                   "ABB.NS",
        "Cummins India":               "CUMMINSIND.NS",
        "Voltas":                      "VOLTAS.NS",
        "Tata Power":                  "TATAPOWER.NS",
        "IRFC":                        "IRFC.NS",
        "Indian Railway Finance":      "IRFC.NS",
        "PFC":                         "PFC.NS",
        "REC Ltd":                     "RECLTD.NS",
        "NHPC":                        "NHPC.NS",
        "SJVN":                        "SJVN.NS",
        "HUDCO":                       "HUDCO.NS",
        "HAL":                         "HAL.NS",
        "BEL":                         "BEL.NS",
        "Bharat Dynamics":             "BDL.NS",
        "Mazagon Dock":                "MAZDOCK.NS",
        "Garden Reach Shipbuilders":   "GRSE.NS",
        "Cochin Shipyard":             "COCHINSHIP.NS",
        "Zydus Lifesciences":          "ZYDUSLIFE.NS",
        "Mankind Pharma":              "MANKIND.NS",
        "Gland Pharma":                "GLAND.NS",
        "Ipca Labs":                   "IPCALAB.NS",
        "Natco Pharma":                "NATCOPHARM.NS",
        "Alkem Labs":                  "ALKEM.NS",
        "Page Industries":             "PAGEIND.NS",
        "Bata India":                  "BATAINDIA.NS",
        "United Spirits":              "MCDOWELL-N.NS",
        "United Breweries":            "UBL.NS",
        "Varun Beverages":             "VBL.NS",
        "Colgate-Palmolive":           "COLPAL.NS",
        "Marico":                      "MARICO.NS",
        "Emami":                       "EMAMILTD.NS",
        "Godrej Agrovet":              "GODREJAGROVET.NS",
        "PI Industries":               "PIIND.NS",
        "Coromandel Intl":             "COROMANDEL.NS",
        "UPL":                         "UPL.NS",
        "Deepak Nitrite":              "DEEPAKNI.NS",
        "Navin Fluorine":              "NAVINFLUOR.NS",
        "SRF Ltd":                     "SRF.NS",
        "Aarti Industries":            "AARTIIND.NS",
        "Laurus Labs":                 "LAURUSLABS.NS",
        "Syngene International":       "SYNGENE.NS",
        "Galaxy Surfactants":          "GALAXYSURF.NS",
        "Fine Organic":                "FINEORG.NS",
        "LTIMindtree":                 "LTIM.NS",
        "Mphasis":                     "MPHASIS.NS",
        "Persistent Systems":          "PERSISTENT.NS",
        "Coforge":                     "COFORGE.NS",
        "Tata Elxsi":                  "TATAELXSI.NS",
        "KPIT Technologies":           "KPITTECH.NS",
        "Birla Soft":                  "BSOFT.NS",
        "Zensar Technologies":         "ZENSARTECH.NS",
        "Mastek":                      "MASTEK.NS",
        "Tanla Platforms":             "TANLA.NS",
        "MapMyIndia":                  "MAPMYINDIA.NS",
        "Info Edge (Naukri)":          "NAUKRI.NS",
        "Just Dial":                   "JUSTDIAL.NS",
        "Indiamart":                   "INDIAMART.NS",
        "Matrimony.com":               "MATRIMONY.NS",
        "Nazara Technologies":         "NAZARA.NS",
        "Star Health Insurance":       "STARHEALTH.NS",
        "ICICI Lombard":               "ICICIGI.NS",
        "ICICI Prudential Life":       "ICICIPRULI.NS",
        "Max Financial":               "MFSL.NS",
        "Can Fin Homes":               "CANFINHOME.NS",
        "LIC Housing Finance":         "LICHSGFIN.NS",
        "PNB Housing Finance":         "PNBHOUSING.NS",
        "Aavas Financiers":            "AAVAS.NS",
        "Home First Finance":          "HOMEFIRST.NS",
        "Aptus Value Housing":         "APTUS.NS",
        "Creditaccess Grameen":        "CREDITACC.NS",
        "Spandana Sphoorty":           "SPANDANA.NS",
        "Bandhan Bank":                "BANDHANBNK.NS",
        "AU Small Finance Bank":       "AUBANK.NS",
        "Ujjivan Small Finance":       "UJJIVANSFB.NS",
        "Equitas Small Finance":       "EQUITASBNK.NS",
        "Suryoday Small Finance":      "SURYODAY.NS",
        "Yes Bank":                    "YESBANK.NS",
        "IDFC First Bank":             "IDFCFIRSTB.NS",
        "Federal Bank":                "FEDERALBNK.NS",
        "South Indian Bank":           "SOUTHBANK.NS",
        "Karur Vysya Bank":            "KARURVYSYA.NS",
        "City Union Bank":             "CUB.NS",
        "DCB Bank":                    "DCBBANK.NS",
        "CSB Bank":                    "CSBBANK.NS",
        "Jammu & Kashmir Bank":        "J&KBANK.NS",
    },

    # ── POPULAR SMALL CAP STOCKS ──────────────────────────────────────
    "🔬 Popular Small Cap Stocks": {
        "Suzlon Energy":               "SUZLON.NS",
        "YES Bank":                    "YESBANK.NS",
        "Vodafone Idea":               "IDEA.NS",
        "RVNL":                        "RVNL.NS",
        "Ircon International":         "IRCON.NS",
        "NBCC":                        "NBCC.NS",
        "HFCL":                        "HFCL.NS",
        "Sterlite Technologies":       "STLTECH.NS",
        "Dixon Technologies":          "DIXON.NS",
        "Amber Enterprises":           "AMBER.NS",
        "Kaynes Technology":           "KAYNES.NS",
        "Syrma SGS":                   "SYRMA.NS",
        "Avalon Technologies":         "AVALON.NS",
        "Krishna Institute":           "KIMS.NS",
        "Rainbow Children":            "RAINBOW.NS",
        "Global Health (Medanta)":     "MEDANTA.NS",
        "Narayana Hrudayalaya":        "NH.NS",
        "Fortis Healthcare":           "FORTIS.NS",
        "Yatharth Hospital":           "YATHARTH.NS",
        "Veritas Finance":             "VERITAS.NS",
        "Capacite Infraprojects":      "CAPACITE.NS",
        "KNR Constructions":           "KNRCON.NS",
        "PNC Infratech":               "PNCINFRA.NS",
        "Ahluwalia Contracts":         "AHLUCONT.NS",
        "Techno Electric":             "TECHNO.NS",
        "Waaree Energies":             "WAAREEENER.NS",
        "Inox Wind":                   "INOXWIND.NS",
        "Websol Energy":               "WESL.NS",
        "Ujaas Energy":                "UJAAS.NS",
        "Borosil Renewables":          "BORORENEW.NS",
        "Premier Energies":            "PREMIERENE.NS",
        "Waaree Renewables":           "WAAREENERGY.NS",
        "Gokaldas Exports":            "GOKALDAS.NS",
        "KPR Mills":                   "KPRMILL.NS",
        "Siyaram Silk Mills":          "SIYSIL.NS",
        "Trident Ltd":                 "TRIDENT.NS",
        "RSWM":                        "RSWM.NS",
        "Chalet Hotels":               "CHALET.NS",
        "Lemon Tree Hotels":           "LEMONTREE.NS",
        "Indian Hotels":               "INDHOTEL.NS",
        "Mahindra Holidays":           "MHRIL.NS",
        "Easy Trip Planners":          "EASEMYTRIP.NS",
        "Thomas Cook India":           "THOMASCOOK.NS",
        "Devyani International":       "DEVYANI.NS",
        "Westlife Foodworld":          "WESTLIFE.NS",
        "Sapphire Foods":              "SAPPHIRE.NS",
        "Restaurant Brands Asia":      "RBA.NS",
    },

    # ── INDIAN ETFs (NSE) ─────────────────────────────────────────────
    "📦 Indian ETFs": {
        "Nippon India Nifty BeES":     "NIFTYBEES.NS",
        "SBI Nifty 50 ETF":            "SETFNIF50.NS",
        "HDFC Nifty 50 ETF":           "HDFCNIFTY.NS",
        "Kotak Nifty 50 ETF":          "KOTAKNIFTY.NS",
        "ICICI Nifty 50 ETF":          "ICICIB22.NS",
        "Nippon India Junior BeES":    "JUNIORBEES.NS",
        "Nippon India Bank BeES":      "BANKBEES.NS",
        "Nippon India IT BeES":        "ITBEES.NS",
        "Nippon India PSU Bank BeES":  "PSUBNKBEES.NS",
        "Nippon India Pharma BeES":    "PHARMABEES.NS",
        "Nippon India Liquid BeES":    "LIQUIDBEES.NS",
        "Mirae Asset Nifty 50 ETF":    "MAFANG.NS",
        "Motilal Nifty Next 50 ETF":   "MOM50.NS",
        "Nippon India Midcap 150 ETF": "NM150BEES.NS",
        "Nippon India Smallcap ETF":   "SETFSMALL.NS",
        "Nippon India Nifty 500 ETF":  "NIF500BEES.NS",
        "HDFC Sensex ETF":             "HDFCSENSEX.NS",
        "SBI Sensex ETF":              "SETFBSE.NS",
        "Nippon India Gold BeES":      "GOLDBEES.NS",
        "HDFC Gold ETF":               "HDFCMFGETF.NS",
        "SBI Gold ETF":                "SBIGETS.NS",
        "Kotak Gold ETF":              "KOTAKGOLD.NS",
        "Axis Gold ETF":               "AXISGOLD.NS",
        "ICICI Gold ETF":              "ICICIGOLD.NS",
        "Nippon India Silver BeES":    "SILVERBEES.NS",
        "Mirae Asset Silver ETF":      "SILVERETF.NS",
        "Nippon India Nifty Infra ETF":"INFRABEES.NS",
        "Nippon India Consumption ETF":"CONSUMBEES.NS",
        "Nippon India Nifty India Mfg ETF": "MAFSETF.NS",
    },

    # ── PSU / GOVERNMENT STOCKS ───────────────────────────────────────
    "🏛️ PSU & Government Stocks": {
        "ONGC":                        "ONGC.NS",
        "Coal India":                  "COALINDIA.NS",
        "NTPC":                        "NTPC.NS",
        "Power Grid":                  "POWERGRID.NS",
        "BHEL":                        "BHEL.NS",
        "GAIL India":                  "GAIL.NS",
        "Indian Oil":                  "IOC.NS",
        "BPCL":                        "BPCL.NS",
        "HPCL":                        "HINDPETRO.NS",
        "Oil India":                   "OIL.NS",
        "SBI":                         "SBIN.NS",
        "Bank of Baroda":              "BANKBARODA.NS",
        "Punjab National Bank":        "PNB.NS",
        "Canara Bank":                 "CANBK.NS",
        "Union Bank":                  "UNIONBANK.NS",
        "Bank of India":               "BANKINDIA.NS",
        "Indian Bank":                 "INDIANB.NS",
        "LIC of India":                "LICI.NS",
        "GIC Re":                      "GICRE.NS",
        "New India Assurance":         "NIACL.NS",
        "HAL":                         "HAL.NS",
        "BEL":                         "BEL.NS",
        "BHEL":                        "BHEL.NS",
        "Cochin Shipyard":             "COCHINSHIP.NS",
        "Mazagon Dock":                "MAZDOCK.NS",
        "Garden Reach":                "GRSE.NS",
        "BEML":                        "BEML.NS",
        "RVNL":                        "RVNL.NS",
        "IRFC":                        "IRFC.NS",
        "IRCTC":                       "IRCTC.NS",
        "IRCON":                       "IRCON.NS",
        "NBCC":                        "NBCC.NS",
        "NMDC":                        "NMDC.NS",
        "SAIL":                        "SAIL.NS",
        "Hindustan Copper":            "HINDCOPPER.NS",
        "NALCO":                       "NATIONALUM.NS",
        "MOIL":                        "MOIL.NS",
        "NHPC":                        "NHPC.NS",
        "SJVN":                        "SJVN.NS",
        "THDC India":                  "THDCIL.NS",
        "PFC":                         "PFC.NS",
        "REC Ltd":                     "RECLTD.NS",
        "HUDCO":                       "HUDCO.NS",
        "NLC India":                   "NLCINDIA.NS",
        "CONCOR":                      "CONCOR.NS",
        "Shipping Corp":               "SCI.NS",
        "Dredging Corp":               "DREDGECORP.NS",
    },

    # ── WORLD INDICES ─────────────────────────────────────────────────
    "🌍 World Indices": {
        "S&P 500 (USA)":               "^GSPC",
        "NASDAQ 100 (USA)":            "^NDX",
        "Dow Jones (USA)":             "^DJI",
        "Russell 2000 (USA)":          "^RUT",
        "TSX Composite (Canada)":      "^GSPTSE",
        "Bovespa (Brazil)":            "^BVSP",
        "FTSE 100 (UK)":               "^FTSE",
        "DAX (Germany)":               "^GDAXI",
        "CAC 40 (France)":             "^FCHI",
        "EURO STOXX 50":               "^STOXX50E",
        "AEX (Netherlands)":           "^AEX",
        "SMI (Switzerland)":           "^SSMI",
        "IBEX 35 (Spain)":             "^IBEX",
        "FTSE MIB (Italy)":            "FTSEMIB.MI",
        "Nikkei 225 (Japan)":          "^N225",
        "Hang Seng (Hong Kong)":       "^HSI",
        "CSI 300 (China)":             "000300.SS",
        "KOSPI (South Korea)":         "^KS11",
        "ASX 200 (Australia)":         "^AXJO",
        "Straits Times (Singapore)":   "^STI",
        "TWSE (Taiwan)":               "^TWII",
        "Tadawul (Saudi Arabia)":      "^TASI.SR",
    },
}

# Flatten to searchable list
ALL_TICKERS = {}
for cat, items in CATEGORIES.items():
    for name, symbol in items.items():
        ALL_TICKERS[f"{name}  [{cat.split(' ', 1)[1]}]"] = symbol

# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════
st.sidebar.title("⚙️ Parameters")

# Category → instrument drill-down
cat_choice = st.sidebar.selectbox("📂 Category", list(CATEGORIES.keys()))
inst_choice = st.sidebar.selectbox(
    "📌 Instrument",
    list(CATEGORIES[cat_choice].keys())
)
ticker_symbol = CATEGORIES[cat_choice][inst_choice]
selected_name = inst_choice

custom_ticker = st.sidebar.text_input(
    "🔍 Or type any NSE/BSE ticker (overrides above):",
    placeholder="e.g. IRFC.NS  SUZLON.NS  ^NSEBANK"
)
if custom_ticker.strip():
    ticker_symbol = custom_ticker.strip().upper()
    selected_name = ticker_symbol

st.sidebar.markdown(f"**Ticker:** `{ticker_symbol}`")
st.sidebar.markdown("---")

buy_drop_pct  = st.sidebar.slider("📉 BUY when daily drop ≥ (%)",   0.1, 10.0, 1.0, 0.1)
sell_rise_pct = st.sidebar.slider("📈 SELL ALL when rise ≥ (%)",    0.1, 15.0, 2.0, 0.1)
lots_per_buy  = st.sidebar.number_input("🛒 Units bought per trigger", 1, 10000, 1)
initial_capital = st.sidebar.number_input("💵 Starting Capital (₹ or $)", 1000, 100_000_000, 100_000, 1000)

st.sidebar.markdown("---")
cs, ce = st.sidebar.columns(2)
start_date = cs.date_input("Start", value=date.today() - timedelta(days=365 * 3))
end_date   = ce.date_input("End",   value=date.today())

run_btn = st.sidebar.button("🚀 Run Simulation", use_container_width=True, type="primary")

# ══════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════
st.title("📊 Indian Market & World Index — Drop-Buy / Rally-Sell Simulator")
st.caption("Buy every dip, sell every rally. Backtest on 500+ Indian stocks, indices, ETFs, PSUs & world indices.")

if not run_btn:
    st.info("👈  Choose a category → instrument in the sidebar, set your thresholds, then click **Run Simulation**.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
### Strategy Logic
Each trading day:
1. `daily_return = (Close_today / Close_yesterday) − 1`
2. If return ≤ **−buy_drop %** → **BUY** X units at close
3. If return ≥ **+sell_rise %** AND holding → **SELL ALL** at close

Positions accumulate across multiple buy signals and are liquidated all at once on a sell signal.
        """)
    with col2:
        st.markdown("""
### What's Covered
- **Nifty 50** all 50 stocks
- **Mid & Small Cap** popular picks
- **All Sectoral Indices** (Bank, IT, Pharma, Auto…)
- **Broad Indices** (Nifty 50/100/200/500, Sensex…)
- **PSU Stocks** (HAL, ONGC, SBI, IRFC…)
- **Indian ETFs** (Gold, Silver, Nifty BeES…)
- **Defence, EV, Renewable energy** themes
- **World Indices** (S&P 500, Nikkei, DAX…)
        """)
    st.stop()

# ══════════════════════════════════════════════════════════════════════
#  FETCH DATA
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def fetch_data(ticker, start, end):
    return yf.download(ticker, start=str(start), end=str(end),
                       progress=False, auto_adjust=True)

with st.spinner(f"Downloading **{selected_name}** (`{ticker_symbol}`) …"):
    raw = fetch_data(ticker_symbol, start_date, end_date)

if raw is None or raw.empty:
    st.error(f"No data for `{ticker_symbol}`. Check ticker / date range.")
    st.stop()

if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.get_level_values(0)

if "Close" not in raw.columns:
    st.error("Could not find Close price column. Try a different ticker.")
    st.stop()

df = raw[["Close"]].copy()
df.index = pd.to_datetime(df.index)
df["Close"] = df["Close"].astype(float)
df = df.dropna()
df["Daily_Return"] = df["Close"].pct_change()

if len(df) < 5:
    st.error("Not enough data. Try a wider date range.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════
#  BACKTEST ENGINE
# ══════════════════════════════════════════════════════════════════════
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

final_price = float(df["Close"].iloc[-1])
open_pnl    = (final_price - float(np.mean(buy_prices))) * lots_held if lots_held > 0 else 0.0
final_value = float(pv_df["Portfolio_Value"].iloc[-1]) if not pv_df.empty else initial_capital

first_price     = float(df["Close"].iloc[1])
bh_values       = initial_capital * (df["Close"].iloc[1:] / first_price)
total_ret_pct   = (final_value - initial_capital) / initial_capital * 100
bh_ret_pct      = (float(bh_values.iloc[-1]) - initial_capital) / initial_capital * 100
num_buys        = sum(1 for t in trades if t["Action"] == "BUY")
num_sells       = sum(1 for t in trades if t["Action"] == "SELL ALL")
total_trade_pnl = float(np.nansum([t.get("Trade P&L", 0) or 0 for t in trades]))

roll_max = pv_df["Portfolio_Value"].cummax()
drawdown = (pv_df["Portfolio_Value"] - roll_max) / roll_max * 100
max_dd   = float(drawdown.min())

# ══════════════════════════════════════════════════════════════════════
#  KPI DASHBOARD
# ══════════════════════════════════════════════════════════════════════
st.markdown("## " + selected_name + "  `" + ticker_symbol + "`  |  " + cat_choice)
st.caption(
    str(start_date) + " to " + str(end_date) +
    "  |  Buy >= -" + str(buy_drop_pct) + "%" +
    "  |  Sell >= +" + str(sell_rise_pct) + "%" +
    "  |  " + str(lots_per_buy) + " unit(s)/buy"
)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("💼 Final Value",       f"{final_value:,.0f}",         f"{total_ret_pct:+.2f}%")
c2.metric("📊 Strategy Return",   f"{total_ret_pct:.2f}%",       "B&H: " + f"{bh_ret_pct:.2f}%")
c3.metric("🏦 Buy & Hold",        f"{bh_ret_pct:.2f}%")
c4.metric("🛒 Buy Signals",        num_buys)
c5.metric("💰 Sell Signals",       num_sells)
c6.metric("📉 Max Drawdown",       f"{max_dd:.2f}%")

c7, c8, c9 = st.columns(3)
c7.metric("✅ Realised P&L",       f"{total_trade_pnl:,.2f}")
c8.metric("📦 Open Lots (Unreal)", str(lots_held) + "  (" + f"{open_pnl:+,.2f}" + ")")
c9.metric("💵 Cash Remaining",     f"{cash:,.2f}")

# ══════════════════════════════════════════════════════════════════════
#  CHARTS
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("📈 Equity Curve & Trade Signals")

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    row_heights=[0.50, 0.30, 0.20],
    vertical_spacing=0.04,
    subplot_titles=("Portfolio Value vs Buy & Hold", "Price + Trade Signals", "Daily Return (%)"),
)

fig.add_trace(go.Scatter(x=pv_df.index, y=pv_df["Portfolio_Value"],
    name="Strategy", line=dict(color="#60a5fa", width=2)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index[1:], y=bh_values,
    name="Buy & Hold", line=dict(color="#f59e0b", width=2, dash="dash")), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df["Close"],
    name="Price", line=dict(color="#a78bfa", width=1.5)), row=2, col=1)

buy_trades  = [t for t in trades if t["Action"] == "BUY"]
sell_trades = [t for t in trades if t["Action"] == "SELL ALL"]

if buy_trades:
    fig.add_trace(go.Scatter(
        x=[t["Date"] for t in buy_trades], y=[t["Price"] for t in buy_trades],
        mode="markers", name="BUY",
        marker=dict(symbol="triangle-up", color="#4ade80", size=10,
                    line=dict(width=1, color="#166534")),
    ), row=2, col=1)

if sell_trades:
    fig.add_trace(go.Scatter(
        x=[t["Date"] for t in sell_trades], y=[t["Price"] for t in sell_trades],
        mode="markers", name="SELL ALL",
        marker=dict(symbol="triangle-down", color="#f87171", size=12,
                    line=dict(width=1, color="#991b1b")),
    ), row=2, col=1)

ret_series = df["Daily_Return"].iloc[1:] * 100
bar_colors = ["#4ade80" if v >= 0 else "#f87171" for v in ret_series]
fig.add_trace(go.Bar(x=df.index[1:], y=ret_series,
    marker_color=bar_colors, showlegend=False), row=3, col=1)
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

# Drawdown
st.subheader("📉 Drawdown")
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

# ══════════════════════════════════════════════════════════════════════
#  TRADE LOG
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("📋 Trade Log")

if trades:
    trade_df = pd.DataFrame(trades)
    trade_df["Date"] = pd.to_datetime(trade_df["Date"]).dt.date

    def hl_action(val):
        if val == "BUY":      return "color: #4ade80; font-weight: bold;"
        if val == "SELL ALL": return "color: #f87171; font-weight: bold;"
        return ""

    def hl_pnl(val):
        if pd.isna(val): return ""
        try:   return "color: #4ade80;" if float(val) >= 0 else "color: #f87171;"
        except: return ""

    fmt = {
        "Price":            "{:.4f}",
        "Cash After":       "{:,.2f}",
        "Daily Return (%)": "{:+.3f}",
        "Avg Buy Price":    "{:.4f}",
        "Trade P&L":        "{:+,.2f}",
    }
    styled = (
        trade_df.style
        .applymap(hl_action, subset=["Action"])
        .applymap(hl_pnl,    subset=["Trade P&L"])
        .format(fmt, na_rep="—")
    )
    st.dataframe(styled, use_container_width=True, height=360)
    csv_data = trade_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Trade Log (CSV)", csv_data, "trade_log.csv", "text/csv")
else:
    st.info("No trades triggered. Try lowering buy threshold or raising sell threshold.")

# ══════════════════════════════════════════════════════════════════════
#  MONTHLY HEATMAP
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("🗓️ Monthly Portfolio Return Heatmap")

if not pv_df.empty:
    pv_m  = pv_df["Portfolio_Value"].resample("ME").last()
    m_ret = pv_m.pct_change().dropna() * 100
    mn    = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    pivot = pd.DataFrame({
        "Return": m_ret.values,
        "Year":   m_ret.index.year,
        "Month":  m_ret.index.month,
    }).pivot(index="Year", columns="Month", values="Return")
    pivot.columns = [mn[m - 1] for m in pivot.columns]

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

# ══════════════════════════════════════════════════════════════════════
#  PRICE STATISTICS TABLE
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("📊 Price Statistics")

stats = {
    "Start Price":     df["Close"].iloc[1],
    "End Price":       df["Close"].iloc[-1],
    "All-Time High":   df["Close"].max(),
    "All-Time Low":    df["Close"].min(),
    "Avg Daily Return":df["Daily_Return"].mean() * 100,
    "Volatility (Ann)":df["Daily_Return"].std() * np.sqrt(252) * 100,
    "Positive Days %": (df["Daily_Return"] > 0).mean() * 100,
    "Negative Days %": (df["Daily_Return"] < 0).mean() * 100,
    "Total Trading Days": len(df),
}
stats_df = pd.DataFrame(list(stats.items()), columns=["Metric", "Value"])
st.dataframe(stats_df.style.format({"Value": lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)}),
             use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("⚠️ For educational/backtesting purposes only. Not financial advice. Data via yfinance.")
