
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import concurrent.futures
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="GEMA v68 TOTAL ARSENAL", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Courier New', monospace; }
    
    /* BOTÓN LANZAR RADAR */
    div.stButton > button { 
        width: 100%; border: 2px solid #00e676; background-color: #161b22; 
        color: #00e676; font-weight: bold; font-size: 18px; padding: 12px; border-radius: 8px;
    }
    
    /* TABLA BLANCA ESTILO IMAGEN 2 */
    .white-table table {
        background-color: white !important;
        color: black !important;
        width: 100%;
        border-collapse: collapse;
    }
    .white-table th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #ccc !important; text-transform: uppercase; }
    .white-table td { border: 1px solid #eee !important; color: black !important; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- 2. EL ARSENAL TOTAL (S&P 500, NASDAQ, IBEX, DAX, DOW, RUSSELL) ---
universos = {
    "🇺🇸 NASDAQ 100": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST", "CSCO", "TMUS", "ADBE", "NFLX", "QCOM", "TXN", "AMD", "INTU", "INTC", "AMAT", "ISRG", "BKNG", "HON", "MDLZ", "VRTX", "ADP", "ADI", "LRCX", "REGN", "PANW", "SNPS", "MU", "KLAC", "CDNS", "MELI", "MAR", "ORLY", "CTAS", "ASML", "PYPL", "MNST", "FTNT", "KDP", "LULU", "WDAY", "ADSK", "NXPI", "EXC", "PCAR", "ROST", "PAYX", "MCHP", "CPRT", "SBUX", "IDXX", "AEP", "BKR", "KHC", "AZN", "GILD", "BIIB", "PDD", "TEAM", "MSTR", "EBAY", "JD", "LCID", "DDOG", "ZS", "CRWD", "RIVN", "BIDU", "SIRI", "ZM", "ALGN", "ENPH"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "CABK.MC", "ACS.MC", "FER.MC", "AENA.MC", "AMS.MC", "ANA.MC", "BKT.MC", "CLNX.MC", "ELE.MC", "ENG.MC", "FDR.MC", "GRF.MC", "IAG.MC", "IDR.MC", "MAP.MC", "MRL.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "UNI.MC", "VIS.MC", "MEL.MC", "SAB.MC", "LOG.MC", "COL.MC", "ACX.MC", "MTS.MC", "PHM.MC"],
    "🇺🇸 S&P 500 (TOTAL)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "TSLA", "UNH", "LLY", "JPM", "XOM", "V", "MA", "PG", "AVGO", "HD", "CVX", "ABBV", "KO", "MRK", "PEP", "COST", "TMO", "MCD", "ADBE", "WMT", "CSCO", "CRM", "PFE", "BAC", "ACN", "ABT", "LIN", "NFLX", "ORCL", "AMD", "TXN", "PM", "INTC", "VZ", "HON", "DIS", "T", "UPS", "NEE", "BMY", "LOW", "SPGI", "RTX", "CAT", "AMGN", "GE", "IBM", "UNP", "GS", "INTU", "DE", "PLD", "AXP", "MS", "ELV", "GILD", "SYK", "AMT", "LMT", "BLK", "MDLZ", "CVS", "BKNG", "ISRG", "ADI", "ADP", "TJX", "MMC", "VRTX", "CI", "REGN", "ZTS", "BSX", "CUBE", "BKR", "ADSK", "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMAT", "AMCR", "AMP", "AMT", "AON", "APA", "APD", "APH", "APTV", "ARE", "ATO", "AVB", "AVY", "AWK", "AXON", "AYI", "AZO", "BA", "BALL", "BBWI", "BBY", "BDX", "BEN", "BF-B", "BG", "BIIB", "BIO", "BK", "BKR", "BLDR", "BLK", "BMY", "BR", "BRO", "BWA", "BX", "BXP", "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCL", "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "COST", "CPB", "CPRT", "CPT", "CRL", "CRM", "CSGP", "CSL", "CSX", "CTAS", "CTLT", "CTRA", "CTSH", "CTVA", "CZR", "D", "DAL", "DAN", "DD", "DFS", "DG", "DGX", "DHI", "DHR", "DLR", "DLTR", "DOCU", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN", "ETR", "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FCX", "FDS", "FDX", "FE", "FFIV", "FI", "FICO", "FIS", "FITB", "FLT", "FMC", "FOX", "FOXA", "FRT", "FSLR", "FTNT", "FTV", "GD", "GEHC", "GEN", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GPC", "GPN", "GRMN", "GWRE", "GWW", "HAL", "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUM", "HWM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INDV", "INVH", "IP", "IPG", "IQV", "IR", "IRM", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KDP", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LULU", "LUV", "LVS", "LW", "LYB", "LYV", "MA", "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "METP", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", "MO", "MOH", "MOS", "MPC", "MPWR", "MRNA", "MSCI", "MSI", "MTB", "MTCH", "MTD", "MU", "NCLH", "NDAQ", "NDSN", "NEE", "NEM", "NI", "NKE", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVR", "NWS", "NWSA", "NXPI", "O", "ODFL", "OKE", "OMC", "ON", "ORLY", "OTIS", "OXY", "PANW", "PARA", "PAYC", "PAYX", "PCAR", "PCG", "PEAK", "PEG", "PFG", "PGR", "PH", "PHM", "PKG", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PYPL", "QCOM", "QRVO", "RCL", "RE", "REG", "RF", "RHI", "RJF", "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RVTY", "SBAC", "SBUX", "SCHW", "SHW", "SJM", "SLB", "SNA", "SNPS", "SO", "SPG", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYY", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGT", "TJX", "TMUS", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXT", "TYL", "UAL", "UDR", "UHS", "ULTA", "UNP", "URI", "USB", "VFC", "VICI", "VLO", "VMC", "VNO", "VRSK", "VRSN", "VTR", "VTRS", "WAB", "WAT", "WBA", "WBD", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WRB", "WRK", "WST", "WTW", "WY", "WYNN", "XEL", "XRAY", "XYL", "YUM", "ZBH", "ZBRA"],
    "🇺🇸 DOW JONES 30": ["MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS", "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PG", "CRM", "TRV", "UNH", "VZ", "V", "WMT", "AMZN"],
    "🇩🇪 DAX 40": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "VOW3.DE", "MUV2.DE", "DHL.DE", "DBK.DE", "EOAN.DE", "RWE.DE", "IFX.DE", "BAYN.DE", "HEI.DE", "CON.DE", "MRK.DE", "BEI.DE", "ADS.DE", "DB1.DE", "SY1.DE", "VNA.DE", "DTG.DE", "HEN3.DE", "PAH3.DE", "MTX.DE", "LIN.DE", "BNR.DE", "ZAL.DE", "FRE.DE", "FME.DE", "QIA.DE", "PUM.DE", "SHL.DE"],
    "🚜 RUSSELL 2000 (SELECT)": ["IWM", "TNA", "MSTR", "ELF", "CROX", "CVNA", "UPST", "AI", "IONQ", "JOBY", "QS", "SPCE", "OPEN", "GME", "AMC", "TLRY", "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES", "COP", "EOG", "VLO", "MPC", "PSX", "KMI", "WMB", "ET", "EPD", "MPLX", "PAA", "VNOM", "OIH", "XOP", "AMLP", "USO", "UNG", "BOIL", "KOLD", "GUSH", "NUGT", "DUST", "JNUG", "JDST", "LIT", "URA", "REMX", "COPX", "SLX", "FAN", "GRID", "BATT", "DRIV", "KARS", "HAIL", "IDRV", "VCAR", "FUV", "SOLO", "WKHS", "RIDE", "GOEV", "HYLN", "XL", "UWMC", "RKT", "LDI", "PFSI", "GHIV", "IVR", "MFA", "NYMT", "MITT", "TWO", "ARR", "CIM", "EARN", "ORC", "AGNC", "NLY", "STWD", "BXMT", "ABR", "RC", "GPMT", "KREF", "LADR", "TRTX", "ACRE", "ARI", "XAN", "CLNC", "HMG", "HASI", "SAFE", "STAR", "GTY", "NNN", "O", "WPC", "STAG", "ADC", "EPR", "VICI", "GLPI", "MGP", "IRT", "MAA", "CPT", "ESS", "AVB", "EQR", "UDR", "AIV", "INVH", "AMH", "TCON", "UMH", "SUI", "ELS", "CUBE", "EXR", "PSA", "LSI", "NSA", "COLD", "DLR", "EQIX", "COR", "CONE", "QTS", "AMT", "CCI", "SBAC", "UNIT", "LAMR", "OUT", "WY", "PCH", "RYN", "CTT", "LAND", "FPI", "AGM"]
}

# --- 3. LÓGICA DE BÚSQUEDA v22 SOUL ---
def check_vela_v22(df, idx=-1):
    if len(df) < abs(idx)+2 or 'K' not in df.columns: return False, "", 0
    curr = df.iloc[idx]; prev = df.iloc[idx-1]
    mid_prev = (prev['High'] + prev['Low']) / 2
    es_buy = (curr['Low'] < prev['Low']) and (curr['Close'] > mid_prev) and (curr['K'] < 20.0)
    es_sell = (curr['High'] > prev['High']) and (curr['Close'] < mid_prev) and (curr['K'] > 80.0)
    if es_buy: return True, "ALCISTA 🟢", curr['K']
    if es_sell: return True, "BAJISTA 🔴", curr['K']
    return False, "", 0

def analizar_full(ticker, strategy):
    try:
        df_d = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        df_w = yf.download(ticker, period="3y", interval="1wk", progress=False, auto_adjust=True)
        df_m = yf.download(ticker, period="5y", interval="1mo", progress=False, auto_adjust=True)
        if df_w.empty: return None

        for d in [df_d, df_w, df_m]:
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            m = d.ta.macd(fast=12, slow=26, signal=9)
            d['MACD'], d['Signal'] = m.iloc[:, 0], m.iloc[:, 1]
            d['K'] = d.ta.stoch(k=14, d=3).iloc[:, 0]

        precio = round(df_d.iloc[-1]['Close'], 2)

        if strategy == "💎 PREMIUM (v22)":
            cm = df_m.iloc[-1]; pm = df_m.iloc[-2]
            m_ok = (cm['MACD'] > cm['Signal']) and (cm['MACD'] > pm['MACD'])
            for i in range(5):
                es, t, k = check_vela_v22(df_w, -1-i)
                if m_ok and es and "ALCISTA" in t:
                    return {"Ticker": ticker, "Señal": f"BUY PREMIUM (Hace {i} sem)", "Precio": precio, "Stoch": round(k,1)}
        else:
            for i in range(5):
                es, t, k = check_vela_v22(df_w, -1-i)
                if es: return {"Ticker": ticker, "Señal": f"{t} (Hace {i} sem)", "Precio": precio, "Stoch": round(k,1)}
        return None
    except: return None

# --- 4. INTERFAZ ---
st.title("🦅 Macdelorean v68 - EL ARSENAL DEFINITIVO")
c1, c2 = st.columns(2)
with c1:
    idx_sel = st.selectbox("📂 Escuadrón Seleccionado:", list(universos.keys()))
with c2:
    estrat_sel = st.selectbox("🧠 Estrategia:", ["🕯️ VELAS DE ENGAÑO", "💎 PREMIUM (v22)"])

if st.button("🔥 LANZAR RADAR"):
    activos = universos[idx_sel]
    encontrados = []
    prog = st.progress(0)
    status = st.empty()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(analizar_full, t, estrat_sel): t for t in activos}
        for i, f in enumerate(concurrent.futures.as_completed(futures)):
            res = f.result()
            if res: encontrados.append(res)
            prog.progress((i+1)/len(activos))
            status.text(f"📡 Analizando {i+1}/{len(activos)}: {futures[f]}")

    if encontrados:
        df_res = pd.DataFrame(encontrados)
        st.download_button("📥 DESCARGAR A EXCEL (CSV)", df_res.to_csv(index=False), "gema_total_report.csv", "text/csv")
        st.markdown('<div class="white-table">', unsafe_allow_html=True)
        st.write(df_res.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Sin señales hoy.")






