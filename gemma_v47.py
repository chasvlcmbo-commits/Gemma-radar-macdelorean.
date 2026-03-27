import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import concurrent.futures

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA ARCHITECT v47", page_icon="🦅", layout="wide")

# --- ESTILOS VISUALES (ADN Macdelorean v22) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Courier New', monospace; }
    div.stButton > button { 
        width: 100%; border: 1px solid #00e676; background-color: #161b22; 
        color: #00e676; font-weight: bold; font-size: 18px; padding: 12px;
    }
    div.stButton > button:hover { background-color: #00e676; color: #000; }
    .stTabs [aria-selected="true"] { background-color: #00e676; color: black !important; }
    .signal-up { color: #00ff88; font-weight: bold; }
    .signal-down { color: #ff3344; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. EL GRAN ARSENAL (+500 ACTIVOS REALES)
# ==============================================================================
universos = {
    "🇺🇸 NASDAQ 100": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST", "CSCO", "TMUS", "ADBE", "NFLX", "QCOM", "TXN", "AMD", "INTU", "INTC", "AMAT", "ISRG", "BKNG", "HON", "MDLZ", "VRTX", "ADP", "ADI", "LRCX", "REGN", "PANW", "SNPS", "MU", "KLAC", "CDNS", "MELI", "MAR", "ORLY", "CTAS", "ASML", "PYPL", "MNST", "FTNT", "KDP", "LULU", "WDAY", "ADSK", "NXPI", "EXC", "MCHP", "KHC", "AEP", "CPRT", "SBUX", "PAYX", "IDXX", "ROST", "MRVL", "ODFL", "AZN", "GILD", "BKR", "BIIB", "TEAM", "MSTR", "PDD", "EBAY", "JD", "LCID", "DDOG", "ZS", "CRWD", "TEAM", "LCID", "RIVN", "PDD", "JD", "BIDU", "SIRI", "ZM", "EBAY", "ALGN", "ENPH"],
    "🇺🇸 S&P 500 (TOP SECTOR)": ["JPM", "V", "MA", "PG", "HD", "CVX", "KO", "DIS", "WMT", "UNH", "CAT", "BA", "XOM", "BAC", "LLY", "ABBV", "PFE", "TMO", "MCD", "NKE", "LIN", "PM", "GS", "HON", "ORCL", "ACN", "RTX", "UPS", "GE", "BRK-B", "UBER", "ABNB", "PLTR", "SOFI", "AFRM", "HOOD", "DKNG"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "CABK.MC", "ACS.MC", "FER.MC", "AENA.MC", "AMS.MC", "ANA.MC", "BKT.MC", "CLNX.MC", "ELE.MC", "ENG.MC", "FDR.MC", "GRF.MC", "IAG.MC", "IDR.MC", "MAP.MC", "MRL.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "UNI.MC", "VIS.MC", "MEL.MC", "SAB.MC", "LOG.MC", "COL.MC"],
    "🇪🇺 EUROPA (DAX/CAC/MIB)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "VOW3.DE", "MC.PA", "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA", "AIR.PA", "SU.PA", "BNP.PA", "RACE.MI", "ENI.MI", "ISP.MI", "UCG.MI", "STLAM.MI", "G.MI", "ENEL.MI"],
    "🚜 RUSSELL 2000 (LÍQUIDOS)": ["IWM", "TNA", "URTY", "SMH", "SOXX", "XBI", "KWEB", "EWZ", "EEM", "GDX", "GDXJ", "SIL", "TAN", "ICLN", "PBW", "MSTR", "ELF", "CROX", "CVNA", "UPST", "AI", "IONQ", "JOBY", "QS", "SPCE", "OPEN", "NKLA", "SAVA", "GME", "AMC", "TLRY", "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES", "COP", "EOG", "PXD", "FANG", "VLO", "MPC", "PSX", "KMI", "WMB", "ET", "EPD", "MPLX", "PAA", "VNOM", "OIH", "XOP", "AMLP", "USO", "UNG", "BOIL", "KOLD", "GUSH", "DRIP", "ERX", "ERY", "NUGT", "DUST", "JNUG", "JDST", "LIT", "URA", "REMX", "COPX", "SLX", "FAN", "GRID", "BATT", "DRIV", "KARS", "HAIL", "IDRV", "VCAR", "FUV", "SOLO", "WKHS", "RIDE", "GOEV", "HYLN", "XL", "UWMC", "RKT", "LDI", "PFSI", "GHIV", "IVR", "MFA", "NYMT", "MITT", "TWO", "ARR", "CIM", "EARN", "ORC", "AGNC", "NLY", "STWD", "BXMT", "ABR", "RC", "GPMT", "KREF", "LADR", "TRTX", "ACRE", "ARI", "XAN", "CLNC", "HMG", "HASI", "SAFE", "STAR", "GTY", "NNN", "O", "WPC", "STAG", "ADC", "EPR", "VICI", "GLPI", "MGP", "IRT", "MAA", "CPT", "ESS", "AVB", "EQR", "UDR", "AIV", "INVH", "AMH", "TCON", "UMH", "SUI", "ELS", "CUBE", "EXR", "PSA", "LSI", "NSA", "COLD", "DLR", "EQIX", "COR", "CONE", "QTS", "AMT", "CCI", "SBAC", "UNIT", "LAMR", "OUT", "WY", "PCH", "RYN", "CTT", "LAND", "FPI", "AGM"],
    "₿ CRIPTOS / COMMOS": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "GC=F", "SI=F", "CL=F", "HG=F"]
}

# ==============================================================================
# 2. INTELIGENCIA DE ESTRATEGIAS
# ==============================================================================
def analizar(ticker, interval, strategy):
    try:
        df = yf.download(ticker, period="3y", interval=interval, progress=False)
        if df is None or len(df) < 30: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9']
        df['Hist'] = macd['MACDh_12_26_9']
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch['STOCHk_14_3_3']

        if strategy == "Velas de Cambio":
            for i in range(1, 9):
                curr, prev = df.iloc[-i], df.iloc[-(i+1)]
                mid_prev = (prev['High'] + prev['Low']) / 2
                sig = ""
                if curr['Low'] < prev['Low'] and curr['Close'] > mid_prev and curr['K'] < 30: sig = "COMPRA (Barrido) 🟢"
                elif curr['High'] > prev['High'] and curr['Close'] < mid_prev and curr['K'] > 70: sig = "VENTA (Barrido) 🔴"
                if sig:
                    return {"TICKER": f"**{ticker}**", "SEÑAL": f"<span class='{'signal-up' if '🟢' in sig else 'signal-down'}'>{sig}</span>", "VELAS": i-1, "MACD (0)": "Alcista" if float(curr['MACD']) > 0 else "Bajista", "CIERRE": round(float(curr['Close']), 2)}

        elif strategy == "Divergencias MACD":
            curr, prev = df.iloc[-1], df.iloc[-5] # Comparar actual con hace 5 velas
            # Divergencia Alcista: Precio cae, MACD sube
            if curr['Low'] < prev['Low'] and curr['MACD'] > prev['MACD'] and curr['K'] < 40:
                return {"TICKER": f"**{ticker}**", "SEÑAL": "<span class='signal-up'>DIVERGENCIA ALCISTA 📈</span>", "VELAS": "Actual", "MACD (0)": "N/A", "CIERRE": round(float(curr['Close']), 2)}
            # Divergencia Bajista: Precio sube, MACD cae
            if curr['High'] > prev['High'] and curr['MACD'] < prev['MACD'] and curr['K'] > 60:
                return {"TICKER": f"**{ticker}**", "SEÑAL": "<span class='signal-down'>DIVERGENCIA BAJISTA 📉</span>", "VELAS": "Actual", "MACD (0)": "N/A", "CIERRE": round(float(curr['Close']), 2)}

        return None
    except: return None

# ==============================================================================
# 3. INTERFAZ PROFESIONAL
# ==============================================================================
st.title("🦅 GEMA ARCHITECT v47")
st.subheader("BARRIDO GLOBAL + DIVERGENCIAS")

col_idx, col_temp, col_strat = st.columns(3)
with col_idx:
    indice_sel = st.selectbox("📂 Selecciona Escuadrón:", list(universos.keys()))
    activos = universos[indice_sel]
with col_temp:
    temp = st.radio("⏱️ Temporalidad:", ["Semanal", "Mensual"], horizontal=True)
    intervalo = "1wk" if temp == "Semanal" else "1mo"
with col_strat:
    estrategia = st.selectbox("🧠 Estrategia:", ["Velas de Cambio", "Divergencias MACD"])

st.markdown(f"📡 Radar configurado para **{len(activos)}** objetivos.")

if st.button("🔥 ACTIVAR RADAR"):
    encontrados = []
    prog = st.progress(0)
    status = st.empty()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_ticker = {executor.submit(analizar, t, intervalo, estrategia): t for t in activos}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ticker)):
            t = future_to_ticker[future]
            status.text(f"Analizando {i+1}/{len(activos)}: {t}")
            res = future.result()
            if res: encontrados.append(res)
            prog.progress((i+1)/len(activos))
            
    status.text("✅ ESCANEO COMPLETADO.")
    
    if encontrados:
        st.balloons()
        df_res = pd.DataFrame(encontrados)
        st.write(df_res.to_html(escape=False, index=False), unsafe_allow_html=True)
        csv = df_res.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DESCARGAR CSV", data=csv, file_name=f"gema_{indice_sel}.csv")
    else:
        st.warning("Sin señales claras.")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/29/DeLorean_DMC-12_on_highway_%28cropped%29.jpg")
