import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import concurrent.futures
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA v57 INFINITE ARSENAL", page_icon="🦅", layout="wide")

# --- ESTILOS VISUALES (Tablas Blancas v22 Soul) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Courier New', monospace; }
    div.stButton > button { 
        width: 100%; border: 2px solid #00e676; background-color: #161b22; 
        color: #00e676; font-weight: bold; font-size: 18px; padding: 12px;
        border-radius: 8px;
    }
    .rendered_html table { background-color: white !important; color: #1c1c1c !important; width: 100%; border: 1px solid #dee2e6 !important; }
    .rendered_html th { background-color: #f8f9fa !important; color: #000 !important; font-weight: bold; padding: 12px !important; }
    .rendered_html td { padding: 10px !important; border: 1px solid #dee2e6 !important; font-weight: 500; color: #1c1c1c !important; }
    .prem-buy { color: #1a7f37; font-weight: 900; background-color: #e6ffec; padding: 4px; border-radius: 4px; }
    .prem-sell { color: #d1242f; font-weight: 900; background-color: #ffebe9; padding: 4px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. EL GRAN ARSENAL (LISTAS TOTALES - PROHIBIDO RECORTAR)
# ==============================================================================
universos = {
    "🇺🇸 S&P 500 (TOTAL 500+)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "TSLA", "UNH", "LLY", "JPM", "XOM", "V", "MA", "PG", "AVGO", "HD", "CVX", "ABBV", "KO", "MRK", "PEP", "COST", "TMO", "MCD", "ADBE", "WMT", "CSCO", "CRM", "PFE", "BAC", "ACN", "ABT", "LIN", "NFLX", "ORCL", "AMD", "TXN", "PM", "INTC", "VZ", "HON", "DIS", "T", "UPS", "NEE", "BMY", "LOW", "SPGI", "RTX", "CAT", "AMGN", "GE", "IBM", "UNP", "GS", "INTU", "DE", "PLD", "AXP", "MS", "ELV", "GILD", "SYK", "AMT", "LMT", "BLK", "MDLZ", "CVS", "BKNG", "ISRG", "ADI", "ADP", "TJX", "MMC", "VRTX", "CI", "REGN", "ZTS", "BSX", "CUBE", "BKR", "ADSK", "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMAT", "AMCR", "AMP", "AON", "APA", "APD", "APH", "APTV", "ARE", "ATO", "AVB", "AVY", "AWK", "AXON", "AYI", "AZO", "BA", "BALL", "BBWI", "BBY", "BDX", "BEN", "BF-B", "BG", "BIIB", "BIO", "BK", "BLDR", "BMY", "BR", "BRO", "BWA", "BX", "BXP", "C", "CAG", "CAH", "CARR", "CB", "CBOE", "CBRE", "CCI", "CCL", "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "CPB", "CPRT", "CPT", "CRL", "CSGP", "CSL", "CSX", "CTAS", "CTLT", "CTRA", "CTSH", "CTVA", "CZR", "D", "DAL", "DAN", "DD", "DFS", "DG", "DGX", "DHI", "DHR", "DLR", "DLTR", "DOCU", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN", "ETR", "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FCX", "FDS", "FDX", "FE", "FFIV", "FI", "FICO", "FIS", "FITB", "FLT", "FMC", "FOX", "FOXA", "FRT", "FSLR", "FTNT", "FTV", "GD", "GEHC", "GEN", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GPC", "GPN", "GRMN", "GWRE", "GWW", "HAL", "HAS", "HBAN", "HCA", "HES", "HIG", "HII", "HLT", "HOLX", "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUM", "HWM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INDV", "INVH", "IP", "IPG", "IQV", "IR", "IRM", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "K", "KDP", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KR", "KVUE", "L", "LDOS", "LEN", "LH", "LHX", "LKQ", "LNC", "LNT", "LULU", "LUV", "LVS", "LW", "LYB", "LYV", "MAA", "MAR", "MAS", "MCHP", "MCK", "MCO", "MDT", "MET", "METP", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMM", "MNST", "MO", "MOH", "MOS", "MPC", "MPWR", "MRNA", "MSCI", "MSI", "MTB", "MTCH", "MTD", "MU", "NCLH", "NDAQ", "NDSN", "NEE", "NEM", "NI", "NKE", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVR", "NWS", "NWSA", "NXPI", "O", "ODFL", "OKE", "OMC", "ON", "ORLY", "OTIS", "OXY", "PANW", "PARA", "PAYC", "PAYX", "PCAR", "PCG", "PEAK", "PEG", "PFG", "PGR", "PH", "PHM", "PKG", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PYPL", "QCOM", "QRVO", "RCL", "RE", "REG", "RF", "RHI", "RJF", "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RVTY", "SBAC", "SBUX", "SCHW", "SHW", "SJM", "SLB", "SNA", "SNPS", "SO", "SPG", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYY", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGT", "TJX", "TMUS", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSN", "TT", "TTWO", "TXT", "TYL", "UAL", "UDR", "UHS", "ULTA", "UNP", "URI", "USB", "VFC", "VICI", "VLO", "VMC", "VNO", "VRSK", "VRSN", "VTR", "VTRS", "WAB", "WAT", "WBA", "WBD", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WRB", "WRK", "WST", "WTW", "WY", "WYNN", "XEL", "XRAY", "XYL", "YUM", "ZBH", "ZBRA"],
    "🇺🇸 NASDAQ 100": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "ADBE", "NFLX", "AMD", "QCOM", "TXN", "INTU", "AMAT", "ISRG", "BKNG", "HON", "MU", "ADI", "ADP", "LRCX", "VRTX", "REGN", "PANW", "SNPS", "KLAC", "CDNS", "MELI", "MAR", "ORLY", "CTAS", "ASML", "CSX", "PYPL", "MNST", "FTNT", "KDP", "LULU", "WDAY", "ADSK", "NXPI", "EXC", "PCAR", "ROST", "PAYX", "EA", "CTSH", "FAST", "DLTR", "VRSK", "ODFL", "BKR", "CEG", "DDOG", "ZS", "CRWD", "TEAM", "MSTR", "PDD", "EBAY", "JD", "BIDU", "SIRI", "ZM", "ALGN", "ENPH"],
    "🇪🇸 IBEX 35 (ES)": ["ITX.MC", "SAN.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "CABK.MC", "ACS.MC", "FER.MC", "AENA.MC", "AMS.MC", "ANA.MC", "BKT.MC", "CLNX.MC", "ELE.MC", "ENG.MC", "FDR.MC", "GRF.MC", "IAG.MC", "IDR.MC", "MAP.MC", "MRL.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "UNI.MC", "VIS.MC", "MEL.MC", "SAB.MC", "LOG.MC", "COL.MC"],
    "🇩🇪 DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "VOW3.DE", "MUV2.DE", "DHL.DE", "DBK.DE", "EOAN.DE", "RWE.DE", "IFX.DE", "BAYN.DE", "HEI.DE", "CON.DE", "MRK.DE", "BEI.DE", "ADS.DE", "DB1.DE", "SY1.DE", "VNA.DE", "DTG.DE", "HEN3.DE", "PAH3.DE", "MTX.DE", "LIN.DE", "BNR.DE", "ZAL.DE", "FRE.DE", "FME.DE", "QIA.DE", "PUM.DE", "SHL.DE"],
    "🇫🇷 CAC 40 (FR)": ["MC.PA", "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA", "AIR.PA", "BNP.PA", "SU.PA", "EL.PA", "DG.PA", "AI.PA", "BN.PA", "CS.PA", "KER.PA", "VIV.PA", "ENGI.PA", "CAP.PA", "ML.PA", "ACA.PA", "CA.PA", "SAF.PA", "AXA.PA", "DSY.PA", "STLAP.PA", "RI.PA", "GLE.PA", "ORA.PA", "EN.PA", "LR.PA", "VIE.PA", "SGO.PA", "HO.PA", "ATO.PA", "PUB.PA", "WLN.PA", "URW.PA", "RNO.PA"],
    "🇮🇹 FTSE MIB (IT)": ["RACE.MI", "ENI.MI", "ISP.MI", "UCG.MI", "STLAM.MI", "G.MI", "EGP.MI", "PRY.MI", "ENEL.MI", "TEN.MI", "AZM.MI", "FBK.MI", "A2A.MI", "AMP.MI", "BAMI.MI", "BPER.MI", "CPR.MI", "DIA.MI", "ERG.MI", "INW.MI", "LDO.MI", "MB.MI", "MONC.MI", "PIRC.MI", "PST.MI", "REC.MI", "SFER.MI", "SRG.MI", "STMMI.MI", "TIT.MI", "TRN.MI"],
    "🚜 RUSSELL 2000 (SMALL CAPS)": ["IWM", "TNA", "URTY", "SMH", "SOXX", "XBI", "KWEB", "EWZ", "GDX", "MSTR", "ELF", "CROX", "CVNA", "UPST", "AI", "IONQ", "JOBY", "QS", "SPCE", "OPEN", "GME", "AMC", "TLRY", "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES", "COP", "EOG", "VLO", "MPC", "PSX", "KMI", "WMB", "ET", "EPD", "MPLX", "PAA", "VNOM", "OIH", "XOP", "USO", "UNG", "BOIL", "KOLD", "GUSH", "NUGT", "DUST", "JNUG", "LIT", "URA", "REMX", "COPX", "SLX", "FAN", "GRID", "BATT", "DRIV", "KARS", "HAIL", "IDRV", "VCAR", "UWMC", "RKT", "LDI", "PFSI", "GHIV", "IVR", "MFA", "NYMT", "MITT", "TWO", "ARR", "CIM", "EARN", "ORC", "AGNC", "NLY", "STWD", "BXMT", "ABR", "RC", "GPMT", "KREF", "LADR", "TRTX", "ACRE", "ARI", "XAN", "CLNC", "HMG", "HASI", "SAFE", "STAR", "GTY", "NNN", "O", "WPC", "STAG", "ADC", "EPR", "VICI", "GLPI", "MGP", "IRT", "MAA", "CPT", "ESS", "AVB", "EQR", "UDR", "AIV", "INVH", "AMH", "TCON", "UMH", "SUI", "ELS", "CUBE", "EXR", "PSA", "LSI", "NSA", "COLD", "DLR", "EQIX", "COR", "CONE", "QTS", "AMT", "CCI", "SBAC", "UNIT", "LAMR", "OUT", "WY", "PCH", "RYN", "CTT", "LAND", "FPI", "AGM"]
}

# ==============================================================================
# 2. MOTOR DE ANÁLISIS (EL ALMA DEL v22)
# ==============================================================================
def check_vela_v22(df, idx=-1):
    if len(df) < abs(idx)+2 or 'K' not in df.columns: return False, "", 0
    curr = df.iloc[idx]; prev = df.iloc[idx-1]
    mid_prev = (prev['High'] + prev['Low']) / 2
    
    # Lógica Nison v22: Barrido + Cierre > 50% anterior + Estocástico < 20 o > 80
    es_buy = (curr['Low'] < prev['Low']) and (curr['Close'] > mid_prev) and (curr['K'] < 20.0)
    es_sell = (curr['High'] > prev['High']) and (curr['Close'] < mid_prev) and (curr['K'] > 80.0)
    
    if es_buy: return True, "ALCISTA 🟢", curr['K']
    if es_sell: return True, "BAJISTA 🔴", curr['K']
    return False, "", 0

def analizar_full(ticker, strategy):
    try:
        # Descarga multitemporal estricta (v22 Style)
        df_d = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        df_w = yf.download(ticker, period="3y", interval="1wk", progress=False, auto_adjust=True)
        df_m = yf.download(ticker, period="5y", interval="1mo", progress=False, auto_adjust=True)

        if df_d.empty or df_w.empty or df_m.empty: return None

        for d in [df_d, df_w, df_m]:
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            d.ta.macd(append=True); d.ta.stoch(append=True)
            d.columns = [c.split('_')[0] if 'MACD' in c or 'STOCH' in c else c for c in d.columns]

        precio = round(df_d.iloc[-1]['Close'], 2)

        if strategy == "💎 OPORTUNIDADES PREMIUM (v22 Style)":
            curr_m = df_m.iloc[-1]; prev_m = df_m.iloc[-2]
            # Filtro Mensual v22: MACD a favor y con fuerza
            m_bull = (curr_m['MACD'] > 0) and (curr_m['MACD'] > curr_m['Signal']) and (curr_m['MACD'] > prev_m['MACD'])
            m_bear = (curr_m['MACD'] < 0) and (curr_m['MACD'] < curr_m['Signal']) and (curr_m['MACD'] < prev_m['MACD'])

            for i in range(5):
                es, tipo, k = check_vela_v22(df_w, idx=-1-i)
                if m_bull and es and "ALCISTA" in tipo:
                    return {"Ticker": ticker, "Señal": f"💎 BUY PREMIUM (H {i} sem)", "Precio": precio, "Stoch": round(k,1)}
                if m_bear and es and "BAJISTA" in tipo:
                    return {"Ticker": ticker, "Señal": f"💀 SELL PREMIUM (H {i} sem)", "Precio": precio, "Stoch": round(k,1)}

        elif strategy == "🕯️ VELAS DE ENGAÑO (Simple)":
            es, tipo, k = check_vela_v22(df_w, idx=-1)
            if es: return {"Ticker": ticker, "TF": "Semanal", "Señal": tipo, "Stoch": round(k,1), "Precio": precio}

        return None
    except: return None

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================
st.title("🦅 GEMA v57 - THE INFINITE ARSENAL")
st.caption("FUSIÓN TOTAL v22 + S&P 500 FULL + EUROPA PAÍSES")

c1, c2, c3 = st.columns(3)
with c1:
    idx = st.selectbox("📂 Escuadrón Seleccionado:", list(universos.keys()))
with c2:
    estrat = st.selectbox("🧠 Estrategia:", ["💎 OPORTUNIDADES PREMIUM (v22 Style)", "🕯️ VELAS DE ENGAÑO (Simple)"])
with c3:
    st.metric("Total Activos", len(universos[idx]))

if st.button("🔥 LANZAR BARRIDO TOTAL"):
    activos = universos[idx]
    encontrados = []
    prog = st.progress(0)
    status = st.empty()

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        future_to_ticker = {executor.submit(analizar_full, t, estrat): t for t in activos}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ticker)):
            status.text(f"Analizando {i+1}/{len(activos)}: {future_to_ticker[future]}")
            res = future.result()
            if res: encontrados.append(res)
            prog.progress((i+1)/len(activos))

    status.markdown(f"### ✅ BARRIDO COMPLETADO. {len(encontrados)} SEÑALES.")
    if encontrados:
        st.balloons()
        st.write(pd.DataFrame(encontrados).to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No se han detectado señales bajo los criterios v22.")

st.sidebar.info("Modo: Soul v22 + Infinite Lists. Filtro mensual activado para modo Premium.")

