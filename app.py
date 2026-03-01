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

    # ── INDIAN MUTUAL FUNDS — NIFTY / INDEX FUNDS (ETF listed on NSE) ──
    "🏦 MF — Index & Nifty Funds (ETF)": {
        "Nippon India Nifty 50 BeES ETF":          "NIFTYBEES.NS",
        "SBI Nifty 50 ETF":                        "SETFNIF50.NS",
        "HDFC Nifty 50 ETF":                       "HDFCNIFTY.NS",
        "Kotak Nifty 50 ETF":                      "KOTAKNIFTY.NS",
        "ICICI Pru Nifty 50 ETF":                  "ICICIB22.NS",
        "Axis Nifty 100 ETF":                      "AXISNIFTY.NS",
        "Nippon India Nifty Next 50 Jr BeES":      "JUNIORBEES.NS",
        "Motilal Nifty Next 50 ETF":               "MOM50.NS",
        "Nippon India Nifty 500 ETF":              "NIF500BEES.NS",
        "Mirae Asset NYSE FANG+ ETF":              "MAFANG.NS",
        "Motilal Oswal Nasdaq 100 ETF":            "MOM100.NS",
        "Mirae Asset S&P 500 Top 50 ETF":          "MASPX.NS",
        "Edelweiss US Tech ETF":                   "USTECH.NS",
        "Mirae Asset Hang Seng Tech ETF":          "MIAEHSTECH.NS",
        "Nippon India Nifty Midcap 150 ETF":       "NM150BEES.NS",
        "Motilal Oswal Midcap 100 ETF":            "MOM.NS",
        "Nippon India Nifty Smallcap ETF":         "SETFSMALL.NS",
        "HDFC Sensex ETF":                         "HDFCSENSEX.NS",
        "SBI Sensex ETF":                          "SETFBSE.NS",
        "Kotak Sensex ETF":                        "KOTAKSENSEX.NS",
    },

    # ── INDIAN MUTUAL FUNDS — SECTORAL ETFs ───────────────────────────
    "🏦 MF — Sectoral & Thematic Funds (ETF)": {
        "Nippon India Bank BeES ETF":              "BANKBEES.NS",
        "Kotak Banking ETF":                       "KOTAKBKETF.NS",
        "SBI Banking & Fin Services ETF":          "SETFNIFBK.NS",
        "ICICI Pru Nifty Bank ETF":                "ICICIBANKN.NS",
        "Mirae Asset Banking & Fin ETF":           "MIAEBFETF.NS",
        "Nippon India IT BeES ETF":                "ITBEES.NS",
        "SBI IT ETF":                              "SETFNIT.NS",
        "Nippon India Pharma BeES ETF":            "PHARMABEES.NS",
        "SBI Pharma ETF":                          "SETFNIFPHARMA.NS",
        "Nippon India PSU Bank BeES ETF":          "PSUBNKBEES.NS",
        "Kotak PSU Bank ETF":                      "KOTAKPSUBK.NS",
        "Nippon India Infra BeES ETF":             "INFRABEES.NS",
        "Nippon India Consumption BeES ETF":       "CONSUMBEES.NS",
        "Nippon India Nifty India Mfg ETF":        "MAFSETF.NS",
        "Mirae Asset Healthcare ETF":              "MIAEHEALTHCARE.NS",
        "Motilal Oswal S&P BSE Healthcare ETF":    "MOHEALTHCARE.NS",
        "Kotak Nifty Auto ETF":                    "KOTAKAUTO.NS",
        "ICICI Pru Nifty FMCG ETF":               "ICICIFMCG.NS",
        "Nippon India Nifty Metal BeES ETF":       "METALBEES.NS",
        "ICICI Pru Nifty Realty ETF":              "ICICIREAL.NS",
        "Mirae Asset Nifty India Defence ETF":     "MIAEDEFENCE.NS",
        "Edelweiss Nifty India Defence ETF":       "NIFTYDEFENCE.NS",
        "Bharat 22 ETF (Govt Disinvestment)":      "BHARAT22ETF.NS",
        "CPSE ETF":                                "CPSEETF.NS",
        "Nippon India Energy BeES ETF":            "ENERGYBEES.NS",
        "ICICI Pru Nifty Oil & Gas ETF":           "ICICIOILGAS.NS",
        "Motilal Oswal S&P BSE Low Vol 30 ETF":    "MOLO.NS",
        "DSP Nifty 50 Equal Weight ETF":           "DSPNIFTY.NS",
        "Nippon India Nifty Quality 30 ETF":       "NV20BEES.NS",
        "Nippon India Nifty 100 Low Vol 30 ETF":   "LOWVOLBEES.NS",
        "ICICI Pru Alpha Low Vol 30 ETF":          "ICICIALPLV.NS",
        "DSP Nifty Private Bank ETF":              "DSPNIFTYPB.NS",
        "Axis Financial Services ETF":             "AXISFINSERV.NS",
    },

    # ── INDIAN MUTUAL FUNDS — COMMODITY FUNDS (ETF) ───────────────────
    "🏦 MF — Commodity Funds (Gold / Silver ETF)": {
        "Nippon India Gold BeES ETF":              "GOLDBEES.NS",
        "HDFC Gold ETF":                           "HDFCMFGETF.NS",
        "SBI Gold ETF":                            "SBIGETS.NS",
        "Kotak Gold ETF":                          "KOTAKGOLD.NS",
        "Axis Gold ETF":                           "AXISGOLD.NS",
        "ICICI Pru Gold ETF":                      "ICICIGOLD.NS",
        "UTI Gold ETF":                            "UTIGL.NS",
        "Quantum Gold ETF":                        "QGOLDHALF.NS",
        "Invesco India Gold ETF":                  "IVZINGOLD.NS",
        "Aditya Birla Gold ETF":                   "BSLGOLDETF.NS",
        "DSP World Gold Fund-of-Fund ETF":         "DSPGOLDETF.NS",
        "Canara Robeco Gold Savings ETF":          "CRGOLDETF.NS",
        "Nippon India Silver BeES ETF":            "SILVERBEES.NS",
        "Mirae Asset Silver ETF":                  "SILVERETF.NS",
        "Kotak Silver ETF":                        "KOTAKSILV.NS",
        "ICICI Pru Silver ETF":                    "ICICISILVER.NS",
        "Axis Silver ETF":                         "AXISSILVER.NS",
        "HDFC Silver ETF":                         "HDFC-SILV-ETF.NS",
        "DSP Silver ETF":                          "DSPSILVER.NS",
        "Aditya Birla Silver ETF":                 "BSLSILVERETF.NS",
    },

    # ── INDIAN MUTUAL FUNDS — FOF / FundOfFunds (NAV-based, BSE listed) ─
    "🏦 MF — Fund of Funds (BSE Listed)": {
        "Motilal Oswal Nasdaq 100 FOF":            "0P0001DRGB.BO",
        "Edelweiss Greater China Equity FOF":      "0P0001F88P.BO",
        "DSP World Agriculture FOF":               "0P0000XVVB.BO",
        "Kotak Global Emerging Market FOF":        "0P0000Y8JQ.BO",
        "Franklin India Feeder Franklin US Opps":  "0P0000Y8FU.BO",
        "ICICI Pru US Bluechip Equity FOF":        "0P0001HV9Q.BO",
        "Mirae Asset NYSE FANG+ FOF":              "0P0001I0DW.BO",
        "Navi US Total Stock Market FOF":          "0P0001M4YU.BO",
        "Nippon India US Equity Opp FOF":          "0P0001HWC0.BO",
        "SBI International Access US Equity FOF":  "0P0001IT5E.BO",
        "PGIM India Global Equity Opp FOF":        "0P0001HXF4.BO",
        "Axis Greater China Equity FOF":           "0P0001IYF7.BO",
        "Kotak Pioneer Fund FOF":                  "0P0001IX04.BO",
        "DSP US Flexible Equity FOF":              "0P0000XVVA.BO",
    },

    # ── DIRECT-PLAN MUTUAL FUNDS (NSE MFSS listed) ────────────────────
    "🏦 MF — Equity Funds (NSE/BSE MF Platform)": {
        # Large Cap
        "Axis Bluechip Fund Direct":               "0P0000XVN4.BO",
        "Mirae Asset Large Cap Direct":            "0P0000YHXH.BO",
        "Canara Robeco Bluechip Direct":           "0P0001DKZM.BO",
        "HDFC Top 100 Direct":                     "0P0000XVQS.BO",
        "SBI Bluechip Direct":                     "0P0000YIW1.BO",
        "ICICI Pru Bluechip Direct":               "0P0000YHYL.BO",
        "Kotak Bluechip Direct":                   "0P0000YHXG.BO",
        "Nippon India Large Cap Direct":           "0P0000YHZJ.BO",
        "UTI Nifty 200 Momentum 30 Direct":        "0P0001I6NV.BO",
        # Flexi Cap
        "Parag Parikh Flexi Cap Direct":           "0P0001DKZP.BO",
        "HDFC Flexi Cap Direct":                   "0P0000XVQT.BO",
        "Kotak Flexicap Direct":                   "0P0000YHY7.BO",
        "UTI Flexi Cap Direct":                    "0P0000YIZ8.BO",
        "DSP Flexi Cap Direct":                    "0P0000XVUZ.BO",
        "Franklin India Flexi Cap Direct":         "0P0000Y8FT.BO",
        "SBI Flexi Cap Direct":                    "0P0001F5WC.BO",
        "Mirae Asset Flexi Cap Direct":            "0P0001HWCW.BO",
        # Mid Cap
        "Nippon India Growth Direct":              "0P0000YI38.BO",
        "HDFC Mid-Cap Opps Direct":                "0P0000XVQW.BO",
        "Kotak Emerging Equity Direct":            "0P0000YHY8.BO",
        "Axis Midcap Direct":                      "0P0001DKZK.BO",
        "DSP Midcap Direct":                       "0P0000XVV0.BO",
        "SBI Magnum Midcap Direct":                "0P0000YJIP.BO",
        "Mirae Asset Midcap Direct":               "0P0001HWCU.BO",
        "Edelweiss Midcap Direct":                 "0P0001F8DX.BO",
        # Small Cap
        "Nippon India Smallcap Direct":            "0P0000YI45.BO",
        "HDFC Small Cap Direct":                   "0P0000XVQX.BO",
        "Axis Smallcap Direct":                    "0P0001DKZN.BO",
        "SBI Small Cap Direct":                    "0P0000YK3X.BO",
        "Kotak Smallcap Direct":                   "0P0001DKZL.BO",
        "DSP Small Cap Direct":                    "0P0000XVV1.BO",
        "Canara Robeco Small Cap Direct":          "0P0001DKZN.BO",
        # ELSS / Tax Saving
        "Axis Long Term Equity (ELSS) Direct":     "0P0000XVN3.BO",
        "Mirae Asset Tax Saver Direct":            "0P0001HWCA.BO",
        "Canara Robeco ELSS Tax Saver Direct":     "0P0001DKZQ.BO",
        "DSP Tax Saver Direct":                    "0P0000XVUX.BO",
        "Nippon India Tax Saver Direct":           "0P0000YI33.BO",
        "SBI Long Term Equity Direct":             "0P0000YJA2.BO",
        "HDFC ELSS Tax Saver Direct":              "0P0000XVQR.BO",
        "Kotak Tax Saver Direct":                  "0P0000YHXJ.BO",
        "Franklin India Taxshield Direct":         "0P0000Y8FS.BO",
        "PGIM India ELSS Tax Saver Direct":        "0P0001HWFZ.BO",
        # Thematic
        "Nippon India Consumption Direct":         "0P0000YI2T.BO",
        "SBI Infra Direct":                        "0P0001F7RX.BO",
        "ICICI Pru India Opps Direct":             "0P0001HV9M.BO",
        "Tata India Consumer Direct":              "0P0001HWCY.BO",
        "Nippon India Power & Infra Direct":       "0P0000YI2Y.BO",
        "ICICI Pru Infra Direct":                  "0P0000YHYM.BO",
        "DSP India T.I.G.E.R. Direct":             "0P0000XVUV.BO",
        "Quant Infrastructure Direct":             "0P0001HWFE.BO",
    },

    # ── DEBT / HYBRID MUTUAL FUNDS (BSE listed) ───────────────────────
    "🏦 MF — Debt & Hybrid Funds": {
        # Hybrid
        "HDFC Balanced Advantage Direct":          "0P0000XVQP.BO",
        "ICICI Pru Balanced Advantage Direct":     "0P0000YHYI.BO",
        "Kotak Balanced Advantage Direct":         "0P0001DKZG.BO",
        "SBI Equity Hybrid Direct":                "0P0000YJAP.BO",
        "Mirae Asset Hybrid Equity Direct":        "0P0001HWCV.BO",
        "Canara Robeco Equity Hybrid Direct":      "0P0001DKZR.BO",
        "DSP Equity & Bond Direct":                "0P0000XVUY.BO",
        "Nippon India Equity Hybrid Direct":       "0P0000YI2P.BO",
        "UTI Aggressive Hybrid Direct":            "0P0000YIY6.BO",
        "Axis Equity Hybrid Direct":               "0P0001F88Q.BO",
        # Multi Asset
        "ICICI Pru Multi Asset Direct":            "0P0000YHYJ.BO",
        "Nippon India Multi Asset Direct":         "0P0001I6NW.BO",
        "Tata Multi Asset Opps Direct":            "0P0001HWCZ.BO",
        "Quant Multi Asset Direct":                "0P0001HWFD.BO",
        # Arbitrage
        "Nippon India Arbitrage Direct":           "0P0000YI1L.BO",
        "ICICI Pru Equity Arbitrage Direct":       "0P0000YHTB.BO",
        "Kotak Equity Arbitrage Direct":           "0P0000YHTD.BO",
        "SBI Arbitrage Opps Direct":               "0P0000YJAR.BO",
        # Liquid / Overnight
        "Nippon India Liquid ETF (LiquidBeES)":    "LIQUIDBEES.NS",
        "HDFC Overnight Direct":                   "0P0000XVQN.BO",
        "SBI Overnight Direct":                    "0P0001F7S2.BO",
        "Kotak Overnight Direct":                  "0P0001DKZJ.BO",
        # Short Duration
        "HDFC Short Term Debt Direct":             "0P0000XVQY.BO",
        "ICICI Pru Short Term Direct":             "0P0000YHYW.BO",
        "SBI Short Term Debt Direct":              "0P0000YJAT.BO",
        "Nippon India Short Duration Direct":      "0P0000YI3H.BO",
        # Corporate Bond
        "HDFC Corporate Bond Direct":              "0P0001F7R3.BO",
        "Kotak Corporate Bond Direct":             "0P0001DKZH.BO",
        "Axis Corporate Debt Direct":              "0P0001F88R.BO",
        "Nippon India Corp Bond Direct":           "0P0001HV7X.BO",
        # Gilt
        "SBI Magnum Gilt Direct":                  "0P0000YJAO.BO",
        "HDFC Gilt 10Y Constant Duration":         "0P0001F7R4.BO",
        "ICICI Pru Constant Maturity Gilt":        "0P0001HV8V.BO",
        "Nippon India Gilt Securities Direct":     "0P0000YI3E.BO",
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

st.sidebar.markdown("### 📉 Trigger Thresholds")
buy_drop_pct  = st.sidebar.slider("BUY when daily drop ≥ (%)",  0.1, 10.0, 1.0, 0.1)
sell_rise_pct = st.sidebar.slider("SELL ALL when rise ≥ (%)",   0.1, 15.0, 2.0, 0.1)

st.sidebar.markdown("### 💰 Investment Settings")
invest_per_signal = st.sidebar.number_input(
    "₹ Invest per BUY signal (Year 1)", min_value=100,
    max_value=10_000_000, value=5000, step=500,
    help="Amount (₹) deployed every time a buy signal fires. Increases by step-up % each year."
)
stepup_pct = st.sidebar.slider(
    "📈 Annual Step-Up (%)", min_value=0, max_value=50, value=10, step=1,
    help="Every 1st Jan, your per-signal investment amount increases by this %."
)

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
2. If return ≤ **−buy_drop %** → **INVEST ₹X** at today's NAV/price
   - Units received = ₹X ÷ Price  *(fractional units, just like real MF)*
   - ₹X increases every year by the **step-up %**
3. If return ≥ **+sell_rise %** AND holding units → **SELL ALL** at today's price
4. Repeat — units stack up across multiple buy signals

No fixed starting capital needed — you invest on demand at each dip.
        """)
    with col2:
        st.markdown("""
### What's Covered
- **Nifty 50** — all 50 constituent stocks
- **Mid & Small Cap** — 150+ popular picks
- **All Sectoral Indices** — Bank, IT, Pharma, Auto, Defence…
- **Broad Indices** — Nifty 50/100/200/500, Sensex…
- **PSU Stocks** — HAL, ONGC, SBI, IRFC, PFC…
- **Indian ETFs** — Gold, Silver, Nifty/Sensex BeES…
- **Mutual Funds (ETF)** — Index, Sectoral, Commodity ETFs
- **Mutual Funds (FOF)** — US, China, Global Fund-of-Funds
- **Equity MFs** — Large/Mid/Small Cap, ELSS, Thematic
- **Debt & Hybrid MFs** — Balanced, Liquid, Gilt, Corp Bond
- **World Indices** — S&P 500, Nikkei, DAX, Hang Seng…
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
    if ".BO" in ticker_symbol and "0P0" in ticker_symbol:
        st.info("💡 **Mutual Fund NAV data** via BSE codes may have limited history on yfinance. "
                "Try the ETF-listed equivalents under **MF — Index & Sectoral Funds** categories "
                "for more reliable data (e.g. NIFTYBEES.NS, GOLDBEES.NS).")
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

# ══════════════════════════════════════════════════════════════════════
#  BACKTEST ENGINE  — Amount-based, fractional units, annual step-up
# ══════════════════════════════════════════════════════════════════════
units_held      = 0.0
buy_cost_basis  = []        # list of (units_bought, price)
trades          = []
port_vals       = []

total_invested  = 0.0       # cumulative ₹ invested
total_withdrawn = 0.0       # cumulative ₹ from sells
realised_pnl    = 0.0

buy_thr  = -buy_drop_pct  / 100.0
sell_thr =  sell_rise_pct / 100.0

current_year       = df.index[1].year
current_invest_amt = float(invest_per_signal)

# Pre-build year → ₹ per signal map
year_invest_map = {}
tmp_yr  = df.index[1].year
tmp_amt = float(invest_per_signal)
for _yr in range(tmp_yr, tmp_yr + 30):
    year_invest_map[_yr] = round(tmp_amt, 2)
    tmp_amt *= (1 + stepup_pct / 100.0)

for i in range(1, len(df)):
    today = df.index[i]
    price = float(df["Close"].iloc[i])
    ret   = float(df["Daily_Return"].iloc[i])

    if np.isnan(ret):
        continue

    # Step-up on new year
    if today.year != current_year:
        current_year       = today.year
        current_invest_amt = current_invest_amt * (1 + stepup_pct / 100.0)

    if ret <= buy_thr:
        invest_amt   = current_invest_amt
        units_bought = invest_amt / price
        units_held  += units_bought
        total_invested += invest_amt
        buy_cost_basis.append((units_bought, price))

        total_units_cost = sum(u * p for u, p in buy_cost_basis)
        total_units_sum  = sum(u for u, _ in buy_cost_basis)
        avg_cost = total_units_cost / total_units_sum

        trades.append({
            "Date":                    today,
            "Action":                  "BUY",
            "NAV / Price (Rs)":        round(price, 4),
            "Amount Invested (Rs)":    round(invest_amt, 2),
            "Units Bought":            round(units_bought, 4),
            "Total Units Held":        round(units_held, 4),
            "Avg Cost (Rs)":           round(avg_cost, 4),
            "Daily Return (%)":        round(ret * 100, 3),
            "Cumul Invested (Rs)":     round(total_invested, 2),
            "Trade PnL (Rs)":          float("nan"),
        })

    elif ret >= sell_thr and units_held > 0:
        proceeds = units_held * price
        total_units_cost = sum(u * p for u, p in buy_cost_basis)
        total_units_sum  = sum(u for u, _ in buy_cost_basis)
        avg_cost  = total_units_cost / total_units_sum
        cost_basis = avg_cost * units_held
        pnl        = proceeds - cost_basis

        total_withdrawn += proceeds
        realised_pnl    += pnl

        trades.append({
            "Date":                    today,
            "Action":                  "SELL ALL",
            "NAV / Price (Rs)":        round(price, 4),
            "Amount Invested (Rs)":    float("nan"),
            "Units Bought":            float("nan"),
            "Total Units Held":        0.0,
            "Avg Cost (Rs)":           round(avg_cost, 4),
            "Daily Return (%)":        round(ret * 100, 3),
            "Cumul Invested (Rs)":     round(total_invested, 2),
            "Trade PnL (Rs)":          round(pnl, 2),
        })
        units_held     = 0.0
        buy_cost_basis = []

    port_vals.append({
        "Date":            today,
        "Price":           price,
        "Units_Held":      units_held,
        "Portfolio_Value": units_held * price + total_withdrawn,
        "Total_Invested":  total_invested,
    })

pv_df = pd.DataFrame(port_vals).set_index("Date")

final_price      = float(df["Close"].iloc[-1])
unrealised_value = units_held * final_price
unrealised_pnl   = (unrealised_value
                    - sum(u * p for u, p in buy_cost_basis)) if units_held > 0 else 0.0
total_current_value = total_withdrawn + unrealised_value

net_pnl          = total_current_value - total_invested
total_return_pct = (net_pnl / total_invested * 100) if total_invested > 0 else 0.0

avg_cost_held = (
    sum(u * p for u, p in buy_cost_basis) / sum(u for u, _ in buy_cost_basis)
    if buy_cost_basis else 0.0
)

num_buys  = sum(1 for t in trades if t["Action"] == "BUY")
num_sells = sum(1 for t in trades if t["Action"] == "SELL ALL")

roll_max = pv_df["Portfolio_Value"].cummax()
drawdown = (pv_df["Portfolio_Value"] - roll_max) / roll_max * 100
max_dd   = float(drawdown.min())

years = max((end_date - start_date).days / 365.25, 0.01)
cagr  = ((total_current_value / total_invested) ** (1 / years) - 1) * 100 if total_invested > 0 else 0.0

invest_years = sorted(set(t.year for t in pd.to_datetime(df.index)))
yr_table = [{"Year": yr,
             "Rs per Signal": "Rs " + f"{year_invest_map.get(yr, invest_per_signal):,.0f}"}
            for yr in invest_years]

# ══════════════════════════════════════════════════════════════════════
#  SUMMARY BANNER
# ══════════════════════════════════════════════════════════════════════
st.markdown("## " + selected_name + "  `" + ticker_symbol + "`")
st.caption(
    str(start_date) + " to " + str(end_date) +
    "  |  Buy >= -" + str(buy_drop_pct) + "%" +
    "  |  Sell >= +" + str(sell_rise_pct) + "%" +
    "  |  Start Rs" + f"{invest_per_signal:,}/signal" +
    "  |  Step-up " + str(stepup_pct) + "% p.a."
)

st.markdown("### 💼 Investment Summary")
m1, m2, m3, m4 = st.columns(4)
m1.metric("💸 Total Invested",        "Rs " + f"{total_invested:,.0f}")
m2.metric("📦 Units Still Held",      f"{units_held:,.4f}",
          "Avg cost Rs " + f"{avg_cost_held:,.2f}" if units_held > 0 else "No open position")
m3.metric("📊 Current Market Value",  "Rs " + f"{unrealised_value:,.0f}",
          "Unrealised Rs " + f"{unrealised_pnl:+,.0f}")
m4.metric("🏦 Total Withdrawn",       "Rs " + f"{total_withdrawn:,.0f}",
          "Realised Rs " + f"{realised_pnl:+,.0f}")

st.markdown("### 📈 Returns & Stats")
r1, r2, r3, r4, r5, r6 = st.columns(6)
r1.metric("🎯 Net P&L",        "Rs " + f"{net_pnl:+,.0f}")
r2.metric("📊 Total Return",   f"{total_return_pct:.2f}%")
r3.metric("📅 CAGR (approx)", f"{cagr:.2f}%")
r4.metric("🛒 Buy Signals",    num_buys)
r5.metric("💰 Sell Signals",   num_sells)
r6.metric("📉 Max Drawdown",   f"{max_dd:.2f}%")

with st.expander("📅 Annual Step-Up Schedule — Rs per Buy Signal"):
    st.dataframe(pd.DataFrame(yr_table), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
#  CHARTS
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("📈 Portfolio Value vs Total Invested + Trade Signals")

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    row_heights=[0.50, 0.30, 0.20],
    vertical_spacing=0.04,
    subplot_titles=(
        "Portfolio Value vs Cumulative Invested",
        "NAV / Price + Buy & Sell Signals",
        "Daily Return (%)"
    ),
)

fig.add_trace(go.Scatter(
    x=pv_df.index, y=pv_df["Portfolio_Value"],
    name="Portfolio Value", line=dict(color="#60a5fa", width=2.5),
    fill="tozeroy", fillcolor="rgba(96,165,250,0.08)",
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=pv_df.index, y=pv_df["Total_Invested"],
    name="Total Invested", line=dict(color="#f59e0b", width=2, dash="dot"),
    fill="tozeroy", fillcolor="rgba(245,158,11,0.06)",
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["Close"],
    name="NAV / Price", line=dict(color="#a78bfa", width=1.5),
), row=2, col=1)

buy_trades  = [t for t in trades if t["Action"] == "BUY"]
sell_trades = [t for t in trades if t["Action"] == "SELL ALL"]

if buy_trades:
    fig.add_trace(go.Scatter(
        x=[t["Date"] for t in buy_trades],
        y=[t["NAV / Price (Rs)"] for t in buy_trades],
        mode="markers", name="BUY",
        marker=dict(symbol="triangle-up", color="#4ade80", size=10,
                    line=dict(width=1, color="#166534")),
        text=["Rs " + f"{t['Amount Invested (Rs)']:,.0f}" + " | " +
              f"{t['Units Bought']:.4f} units" for t in buy_trades],
        hovertemplate="%{text}<extra>BUY @ Rs %{y:.2f}</extra>",
    ), row=2, col=1)

if sell_trades:
    fig.add_trace(go.Scatter(
        x=[t["Date"] for t in sell_trades],
        y=[t["NAV / Price (Rs)"] for t in sell_trades],
        mode="markers", name="SELL ALL",
        marker=dict(symbol="triangle-down", color="#f87171", size=13,
                    line=dict(width=1, color="#991b1b")),
        text=["PnL Rs " + f"{t['Trade PnL (Rs)']:+,.0f}" for t in sell_trades],
        hovertemplate="%{text}<extra>SELL @ Rs %{y:.2f}</extra>",
    ), row=2, col=1)

ret_series = df["Daily_Return"].iloc[1:] * 100
bar_colors = ["#4ade80" if v >= 0 else "#f87171" for v in ret_series]
fig.add_trace(go.Bar(
    x=df.index[1:], y=ret_series,
    marker_color=bar_colors, showlegend=False,
), row=3, col=1)
fig.add_hline(y=-buy_drop_pct,  line=dict(color="#4ade80", dash="dot", width=1), row=3, col=1)
fig.add_hline(y=sell_rise_pct,  line=dict(color="#f87171", dash="dot", width=1), row=3, col=1)

fig.update_layout(
    height=750, template="plotly_dark",
    plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    margin=dict(l=55, r=20, t=50, b=20),
    hovermode="x unified",
)
fig.update_yaxes(gridcolor="#1e293b")
fig.update_xaxes(gridcolor="#1e293b")
st.plotly_chart(fig, use_container_width=True)

# Units chart
st.subheader("📦 Units Accumulation Over Time")
uf = go.Figure(go.Scatter(
    x=pv_df.index, y=pv_df["Units_Held"],
    fill="tozeroy", fillcolor="rgba(167,139,250,0.15)",
    line=dict(color="#a78bfa", width=2), name="Units Held",
))
uf.update_layout(
    height=220, template="plotly_dark",
    plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
    margin=dict(l=55, r=20, t=10, b=20),
    yaxis_title="Units Held", showlegend=False,
)
uf.update_yaxes(gridcolor="#1e293b")
uf.update_xaxes(gridcolor="#1e293b")
st.plotly_chart(uf, use_container_width=True)

# Drawdown
st.subheader("📉 Portfolio Drawdown")
dd_fig = go.Figure(go.Scatter(
    x=drawdown.index, y=drawdown,
    fill="tozeroy", fillcolor="rgba(248,113,113,0.15)",
    line=dict(color="#f87171", width=1.5),
))
dd_fig.update_layout(
    height=200, template="plotly_dark",
    plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
    margin=dict(l=55, r=20, t=10, b=20),
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
        "NAV / Price (Rs)":      "{:.4f}",
        "Amount Invested (Rs)":  "{:,.2f}",
        "Units Bought":          "{:.4f}",
        "Total Units Held":      "{:.4f}",
        "Avg Cost (Rs)":         "{:.4f}",
        "Daily Return (%)":      "{:+.3f}",
        "Cumul Invested (Rs)":   "{:,.2f}",
        "Trade PnL (Rs)":        "{:+,.2f}",
    }
    styled = (
        trade_df.style
        .applymap(hl_action, subset=["Action"])
        .applymap(hl_pnl,    subset=["Trade PnL (Rs)"])
        .format(fmt, na_rep="—")
    )
    st.dataframe(styled, use_container_width=True, height=380)
    csv_data = trade_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Trade Log (CSV)", csv_data, "trade_log.csv", "text/csv")
else:
    st.info("No trades triggered. Try adjusting the drop / rise thresholds.")

# ══════════════════════════════════════════════════════════════════════
#  MONTHLY HEATMAP
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Monthly Portfolio Return Heatmap")

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
#  YEAR-WISE TABLE
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Year-wise Investment & Returns")

buy_df_yr = pd.DataFrame([t for t in trades if t["Action"] == "BUY"])
sell_df_yr = pd.DataFrame([t for t in trades if t["Action"] == "SELL ALL"])

if not buy_df_yr.empty:
    buy_df_yr["Year"] = pd.to_datetime(buy_df_yr["Date"]).dt.year
    yr_invested = buy_df_yr.groupby("Year")["Amount Invested (Rs)"].sum()
    yr_signals  = buy_df_yr.groupby("Year").size()

    sell_pnl_yr = pd.Series(dtype=float, name="Trade PnL (Rs)")
    if not sell_df_yr.empty:
        sell_df_yr["Year"] = pd.to_datetime(sell_df_yr["Date"]).dt.year
        sell_pnl_yr = sell_df_yr.groupby("Year")["Trade PnL (Rs)"].sum()

    yr_rows = []
    for yr in yr_invested.index:
        yr_rows.append({
            "Year":              yr,
            "Rs/Signal":         "Rs " + f"{year_invest_map.get(yr, invest_per_signal):,.0f}",
            "Buy Signals":       int(yr_signals.get(yr, 0)),
            "Total Invested":    "Rs " + f"{yr_invested.get(yr, 0):,.0f}",
            "Realised PnL":      "Rs " + f"{sell_pnl_yr.get(yr, 0.0):+,.0f}",
        })
    st.dataframe(pd.DataFrame(yr_rows), use_container_width=True, hide_index=True)

# ── NAV Statistics ────────────────────────────────────────────────────
st.markdown("---")
st.subheader("NAV / Price Statistics")
stats = {
    "Start NAV / Price (Rs)":   df["Close"].iloc[1],
    "End NAV / Price (Rs)":     df["Close"].iloc[-1],
    "All-Time High (Rs)":       df["Close"].max(),
    "All-Time Low (Rs)":        df["Close"].min(),
    "Avg Daily Return (%)":     df["Daily_Return"].mean() * 100,
    "Annualised Volatility (%)":df["Daily_Return"].std() * np.sqrt(252) * 100,
    "Positive Days (%)":        (df["Daily_Return"] > 0).mean() * 100,
    "Negative Days (%)":        (df["Daily_Return"] < 0).mean() * 100,
    "Total Trading Days":       len(df),
}
stats_df = pd.DataFrame(list(stats.items()), columns=["Metric", "Value"])
def fmt_stat(v):
    if isinstance(v, float):
        return f"Rs {v:,.2f}" if abs(v) > 1 else f"{v:.3f}%"
    return str(int(v))
st.dataframe(
    stats_df.style.format({"Value": fmt_stat}),
    use_container_width=True, hide_index=True
)

st.markdown("---")
st.caption("Educational/backtesting simulator only. Not financial advice. Data via yfinance.")
