import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import concurrent.futures
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA v65 ARSENAL TOTAL", page_icon="🦅", layout="wide")

# --- ESTILOS VISUALES (Tabla Blanca + Botón Excel) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Courier New', monospace; }
    div.stButton > button { 
        width: 100%; border: 2px solid #00e676; background-color: #161b22; 
        color: #00e676; font-weight: bold; font-size: 18px; padding: 12px;
        border-radius: 8px; box-shadow: 0 0 10px rgba(0,230,118,0.2);
    }
    .stDownloadButton > button {
        width: 100%; background-color: #1a7f37; color: white; border: none;
        font-weight: bold; padding: 10px; border-radius: 6px;
    }
    /* TABLA BLANCA PROFESIONAL */
    .rendered_html table {
        background-color: white !important;
        color: #1c1c1c !important;
        border-radius: 8px; width: 100%; border: 1px solid #dee2e6 !important;
    }
    .rendered_html th {
        background-color: #f8f9fa !important; color: #000000 !important;
        font-weight: bold; padding: 12px !important; border: 1px solid #dee2e6 !important;
        text-transform: uppercase;
    }
    .rendered_html td {
        color: #1c1c1c !important; padding: 10px !important;
        border: 1px solid #dee2e6 !important; font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. EL GRAN ARSENAL (LISTAS TOTALES SIN RECORTES)
# ==============================================================================
universos = {
    "🇺🇸 DOW JONES 30": ["MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS", "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PG", "CRM", "TRV", "UNH", "VZ", "V", "WMT", "AMZN"],
    "🇺🇸 S&P 500 (TOTAL)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "TSLA", "UNH", "LLY", "JPM", "XOM", "V", "MA", "PG", "AVGO", "HD", "CVX", "ABBV", "KO", "MRK", "PEP", "COST", "TMO", "MCD", "ADBE", "WMT", "CSCO", "CRM", "PFE", "BAC", "ACN", "ABT", "LIN", "NFLX", "ORCL", "AMD", "TXN", "PM", "INTC", "VZ", "HON", "DIS", "T", "UPS", "NEE", "BMY", "LOW", "SPGI", "RTX", "CAT", "AMGN", "GE", "IBM", "UNP", "GS", "INTU", "DE", "PLD", "AXP", "MS", "ELV", "GILD", "SYK", "AMT", "LMT", "BLK", "MDLZ", "CVS", "BKNG", "ISRG", "ADI", "ADP", "TJX", "MMC", "VRTX", "CI", "REGN", "ZTS", "BSX", "CUBE", "BKR", "ADSK", "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMAT", "AMCR", "AMP", "AON", "APA", "APD", "APH", "APTV", "ARE", "ATO", "AVB", "AVY", "AWK", "AXON", "AYI", "AZO", "BA", "BALL", "BBWI", "BBY", "BDX", "BEN", "BF-B", "BG", "BIIB", "BIO", "BK", "BLDR", "BMY", "BR", "BRO", "BWA", "BX", "BXP", "C", "CAG", "CAH", "CARR", "CB", "CBOE", "CBRE", "CCI", "CCL", "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "CPB", "CPRT", "CPT", "CRL", "CRM", "CSGP", "CSL", "CSX", "CTAS", "CTLT", "CTRA", "CTSH", "CTVA", "CZR", "D", "DAL", "DAN", "DD", "DFS", "DG", "DGX", "DHI", "DHR", "DLR", "DLTR", "DOCU", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN", "ETR", "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FCX", "FDS", "FDX", "FE", "FFIV", "FI", "FICO", "FIS", "FITB", "FLT", "FMC", "FOX", "FOXA", "FRT", "FSLR", "FTNT", "FTV", "GD", "GEHC", "GEN", "GILD", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GPC", "GPN", "GRMN", "GWRE", "GWW", "HAL", "HAS", "HBAN", "HCA", "HES", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUM", "HWM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INDV", "INVH", "IP", "IPG", "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KDP", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LULU", "LUV", "LVS", "LW", "LYB", "LYV", "MA", "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "METP", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", "MO", "MOH", "MOS", "MPC", "MPWR", "MRK", "MRNA", "MS", "MSCI", "MSFT", "MSI", "MTB", "MTCH", "MTD", "MU", "NCLH", "NDAQ", "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWS", "NWSA", "NXPI", "O", "ODFL", "OKE", "OMC", "ON", "ORCL", "ORLY", "OTIS", "OXY", "PANW", "PARA", "PAYC", "PAYX", "PCAR", "PCG", "PEAK", "PEG", "PEP", "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PLD", "PM", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PXD", "PYPL", "QCOM", "QRVO", "RCL", "RE", "REG", "REGN", "RF", "RHI", "RJF", "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "RVTY", "SBAC", "SBUX", "SCHW", "SHW", "SIER", "SIVB", "SJM", "SLB", "SNA", "SNPS", "SO", "SPG", "SPGI", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGT", "TJX", "TMO", "TMUS", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXN", "TXT", "TYL", "UAL", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB", "V", "VFC", "VICI", "VLO", "VMC", "VNO", "VRSK", "VRSN", "VRTX", "VTR", "VTRS", "VZ", "WAB", "WAT", "WBA", "WBD", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WMT", "WRB", "WRK", "WST", "WTW", "WY", "WYNN", "XEL", "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZTS"],
    "🇺🇸 NASDAQ 100": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "ADBE", "NFLX", "AMD", "QCOM", "TXN", "INTU", "AMAT", "ISRG", "BKNG", "HON", "MU", "ADI", "ADP", "LRCX", "VRTX", "REGN", "PANW", "SNPS", "KLAC", "CDNS", "MELI", "MAR", "ORLY", "CTAS", "ASML", "CSX", "PYPL", "MNST", "FTNT", "KDP", "LULU", "WDAY", "ADSK", "NXPI", "EXC", "PCAR", "ROST", "PAYX", "EA", "CTSH", "FAST", "DLTR", "VRSK", "ODFL", "BKR", "CEG", "DDOG", "ZS", "CRWD", "TEAM", "MSTR", "PDD", "EBAY", "JD", "BIDU", "SIRI", "ZM", "ALGN", "ENPH"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "CABK.MC", "ACS.MC", "FER.MC", "AENA.MC", "AMS.MC", "ANA.MC", "BKT.MC", "CLNX.MC", "ELE.MC", "ENG.MC", "FDR.MC", "GRF.MC", "IAG.MC", "IDR.MC", "MAP.MC", "MRL.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "UNI.MC", "VIS.MC", "MEL.MC", "SAB.MC", "LOG.MC", "COL.MC"],
    "🇩🇪 DAX 40": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "VOW3.DE", "MUV2.DE", "DHL.DE", "DBK.DE", "EOAN.DE", "RWE.DE", "IFX.DE", "BAYN.DE", "HEI.DE", "CON.DE", "MRK.DE", "BEI.DE", "ADS.DE", "DB1.DE", "SY1.DE", "VNA.DE", "DTG.DE", "HEN3.DE", "PAH3.DE", "MTX.DE", "LIN.DE", "BNR.DE", "ZAL.DE", "FRE.DE", "FME.DE", "QIA.DE", "PUM.DE", "SHL.DE"],
    "🇫🇷 CAC 40": ["MC.PA", "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA", "AIR.PA", "BNP.PA", "SU.PA", "EL.PA", "DG.PA", "AI.PA", "BN.PA", "CS.PA", "KER.PA", "VIV.PA", "ENGI.PA", "CAP.PA", "ML.PA", "ACA.PA", "CA.PA", "SAF.PA", "AXA.PA", "DSY.PA", "STLAP.PA", "RI.PA", "GLE.PA", "ORA.PA", "EN.PA", "LR.PA", "VIE.PA", "SGO.PA", "HO.PA", "ATO.PA", "PUB.PA", "WLN.PA", "URW.PA", "RNO.PA"],
    "🇮🇹 FTSE MIB": ["RACE.MI", "ENI.MI", "ISP.MI", "UCG.MI", "STLAM.MI", "G.MI", "EGP.MI", "PRY.MI", "ENEL.MI", "TEN.MI", "AZM.MI", "FBK.MI", "A2A.MI", "AMP.MI", "BAMI.MI", "BPER.MI", "CPR.MI", "DIA.MI", "ERG.MI", "INW.MI", "LDO.MI", "MB.MI", "MONC.MI", "PIRC.MI", "PST.MI", "REC.MI", "SFER.MI", "SRG.MI", "STMMI.MI", "TIT.MI", "TRN.MI"],
    "🚜 RUSSELL 2000 (TOTAL)": ["IWM", "TNA", "URTY", "SMH", "SOXX", "XBI", "KWEB", "EWZ", "EEM", "GDX", "GDXJ", "SIL", "TAN", "ICLN", "PBW", "MSTR", "ELF", "CROX", "CVNA", "UPST", "AI", "IONQ", "JOBY", "QS", "SPCE", "OPEN", "NKLA", "SAVA", "GME", "AMC", "TLRY", "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES", "COP", "EOG", "PXD", "FANG", "VLO", "MPC", "PSX", "KMI", "WMB", "ET", "EPD", "MPLX", "PAA", "VNOM", "OIH", "XOP", "AMLP", "USO", "UNG", "BOIL", "KOLD", "GUSH", "DRIP", "ERX", "ERY", "NUGT", "DUST", "JNUG", "JDST", "LIT", "URA", "REMX", "COPX", "SLX", "FAN", "GRID", "BATT", "DRIV", "KARS", "HAIL", "IDRV", "VCAR", "FUV", "SOLO", "WKHS", "RIDE", "GOEV", "HYLN", "XL", "UWMC", "RKT", "LDI", "PFSI", "GHIV", "IVR", "MFA", "NYMT", "MITT", "TWO", "ARR", "CIM", "EARN", "ORC", "AGNC", "NLY", "STWD", "BXMT", "ABR", "RC", "GPMT", "KREF", "LADR", "TRTX", "ACRE", "ARI", "XAN", "CLNC", "HMG", "HASI", "SAFE", "STAR", "GTY", "NNN", "O", "WPC", "STAG", "ADC", "EPR", "VICI", "GLPI", "MGP", "IRT", "MAA", "CPT", "ESS", "AVB", "EQR", "UDR", "AIV", "INVH", "AMH", "TCON", "UMH", "SUI", "ELS", "CUBE", "EXR", "PSA", "LSI", "NSA", "COLD", "DLR", "EQIX", "COR", "CONE", "QTS", "AMT", "CCI", "SBAC", "UNIT", "LAMR", "OUT", "WY", "PCH", "RYN", "CTT", "LAND", "FPI", "AGM"]
}

# ==============================================================================
# 2. MOTOR TÉCNICO v22 SOUL
# ==============================================================================
def check_vela_v22_original(df, idx=-1):
    if len(df) < abs(idx)+2 or 'K' not in df.columns: return False, "", 0
    curr = df.iloc[idx]; prev = df.iloc[idx-1]
    mid_prev = (prev['High'] + prev['Low']) / 2
    l_curr, h_curr, c_curr, k = curr['Low'], curr['High'], curr['Close'], curr['K']
    l_prev, h_prev = prev['Low'], prev['High']
    if (l_curr < l_prev) and (c_curr > mid_prev) and (k < 20.0): return True, "ALCISTA 🟢", k
    if (h_curr > h_prev) and (c_curr < mid_prev) and (k > 80.0): return True, "BAJISTA 🔴", k
    return False, "", 0

def analizar_full(ticker, strategy):
    try:
        df_d = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        df_w = yf.download(ticker, period="3y", interval="1wk", progress=False, auto_adjust=True)
        df_m = yf.download(ticker, period="5y", interval="1mo", progress=False, auto_adjust=True)
        if df_d.empty or df_w.empty or df_m.empty: return None
        for df in [df_d, df_w, df_m]:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            if macd is not None:
                df['MACD'] = macd.iloc[:, 0]; df['Signal'] = macd.iloc[:, 1]
            stoch = df.ta.stoch(k=14, d=3)
            if stoch is not None: df['K'] = stoch.iloc[:, 0]
        precio = round(df_d.iloc[-1]['Close'], 2)
        if strategy == "💎 PREMIUM (v22 Style)":
            cm, pm = df_m.iloc[-1], df_m.iloc[-2]
            m_bull = (cm['MACD'] > cm['Signal']) and (cm['MACD'] > pm['MACD'])
            m_bear = (cm['MACD'] < cm['Signal']) and (cm['MACD'] < pm['MACD'])
            for i in range(5):
                es, tipo, k = check_vela_v22_original(df_w, idx=-1-i)
                if m_bull and es and "ALCISTA" in tipo: return {"Ticker": ticker, "Señal": f"BUY PREMIUM (Hace {i} sem)", "Precio": precio, "Stoch": round(k,1)}
                if m_bear and es and "BAJISTA" in tipo: return {"Ticker": ticker, "Señal": f"SELL PREMIUM (Hace {i} sem)", "Precio": precio, "Stoch": round(k,1)}
        else:
            for i in range(5):
                es, tipo, k = check_vela_v22_original(df_w, idx=-1-i)
                if es: return {"Ticker": ticker, "Señal": f"{tipo} (Hace {i} sem)", "Precio": precio, "Stoch": round(k,1)}
        return None
    except: return None

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================
st.title("🦅 GEMA v65 - ARSENAL INFINITO")
c1, c2 = st.columns(2)
with c1:
    idx = st.selectbox("📂 Selecciona Índice:", list(universos.keys()))
with c2:
    estrat = st.selectbox("🧠 Estrategia:", ["💎 PREMIUM (v22 Style)", "🕯️ VELAS DE ENGAÑO"])

excel_placeholder = st.sidebar.empty()

if st.button("🔥 LANZAR RADAR"):
    activos = universos[idx]
    encontrados = []
    prog = st.progress(0)
    status = st.empty()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(analizar_full, t, estrat): t for t in activos}
        for i, f in enumerate(concurrent.futures.as_completed(futures)):
            res = f.result()
            if res: encontrados.append(res)
            prog.progress((i+1)/len(activos))
            status.text(f"Analizando {i+1}/{len(activos)}: {futures[f]}")
    status.markdown(f"### ✅ BARRIDO COMPLETADO. {len(encontrados)} SEÑALES.")
    if encontrados:
        st.balloons()
        df_res = pd.DataFrame(encontrados)
        st.write(df_res.to_html(escape=False, index=False), unsafe_allow_html=True)
        csv = df_res.to_csv(index=False).encode('utf-8')
        excel_placeholder.download_button("📥 DESCARGAR EXCEL", data=csv, file_name=f'gema_{idx}.csv', mime='text/csv')





