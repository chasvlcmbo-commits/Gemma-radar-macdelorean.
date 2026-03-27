
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import concurrent.futures
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA v49 WHITE EDITION", page_icon="🦅", layout="wide")

# --- ESTILOS VISUALES (Fondo oscuro con TABLAS BLANCAS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Courier New', monospace; }
    
    /* Botones Estilo Macdelorean */
    div.stButton > button { 
        width: 100%; border: 2px solid #00e676; background-color: #161b22; 
        color: #00e676; font-weight: bold; font-size: 18px; padding: 12px;
        border-radius: 8px;
    }
    
    /* TABLA BLANCA PROFESIONAL (Como el robot antiguo) */
    .rendered_html table {
        background-color: white !important;
        color: #1c1c1c !important;
        border-radius: 8px;
        overflow: hidden;
        width: 100%;
    }
    .rendered_html th {
        background-color: #f0f2f6 !important;
        color: #1c1c1c !important;
        font-weight: bold;
        padding: 12px !important;
        border: 1px solid #dee2e6 !important;
    }
    .rendered_html td {
        color: #1c1c1c !important;
        padding: 10px !important;
        border: 1px solid #dee2e6 !important;
    }
    
    /* Colores de Señales sobre fondo blanco */
    .sig-up { color: #1a7f37; font-weight: bold; }
    .sig-down { color: #d1242f; font-weight: bold; }
    .prem-buy { color: #1a7f37; font-weight: 800; }
    .prem-sell { color: #d1242f; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. EL GRAN EJÉRCITO (TODOS LOS TICKERS POSIBLES)
# ==============================================================================
universos = {
    "🇺🇸 S&P 500 (FULL SECTOR)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "TSLA", "UNH", "LLY", "JPM", "XOM", "V", "MA", "PG", "AVGO", "HD", "CVX", "ABBV", "KO", "MRK", "PEP", "COST", "TMO", "MCD", "ADBE", "WMT", "CSCO", "CRM", "PFE", "BAC", "ACN", "ABT", "LIN", "NFLX", "ORCL", "AMD", "TXN", "PM", "INTC", "VZ", "HON", "DIS", "T", "UPS", "NEE", "BMY", "LOW", "SPGI", "RTX", "CAT", "AMGN", "GE", "IBM", "UNP", "GS", "INTU", "DE", "PLD", "AXP", "MS", "ELV", "GILD", "SYK", "AMT", "LMT", "BLK", "MDLZ", "CVS", "BKNG", "ISRG", "ADI", "ADP", "TJX", "MMC", "VRTX", "CI", "REGN", "ZTS", "BSX", "CUBE", "BKR"],
    "🇺🇸 NASDAQ 100": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "ADBE", "NFLX", "AMD", "QCOM", "TXN", "INTU", "AMAT", "ISRG", "BKNG", "HON", "MU", "ADI", "ADP", "LRCX", "VRTX", "REGN", "PANW", "SNPS", "KLAC", "CDNS", "MELI", "MAR", "ORLY", "CTAS", "ASML", "CSX", "PYPL", "MNST", "FTNT", "KDP", "LULU", "WDAY", "ADSK", "NXPI", "EXC", "PCAR", "ROST", "PAYX", "EA", "CTSH", "FAST", "DLTR", "VRSK", "ODFL", "BKR", "CEG", "DDOG", "ZS", "CRWD", "TEAM", "MSTR", "PDD", "EBAY", "JD", "BIDU", "SIRI", "ZM", "ALGN", "ENPH"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "CABK.MC", "ACS.MC", "FER.MC", "AENA.MC", "AMS.MC", "ANA.MC", "BKT.MC", "CLNX.MC", "ELE.MC", "ENG.MC", "FDR.MC", "GRF.MC", "IAG.MC", "IDR.MC", "MAP.MC", "MRL.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "UNI.MC", "VIS.MC", "MEL.MC", "SAB.MC", "LOG.MC", "COL.MC"],
    "🇪🇺 EUROPA (CAC/DAX/MIB)": ["MC.PA", "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA", "AIR.PA", "BNP.PA", "SU.PA", "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "VOW3.DE", "RACE.MI", "ENI.MI", "ISP.MI", "UCG.MI", "STLAM.MI", "G.MI", "ENEL.MI", "PRY.MI"],
    "🚜 RUSSELL 2000 (SMALL CAPS)": ["IWM", "TNA", "URTY", "SMH", "SOXX", "XBI", "KWEB", "EWZ", "GDX", "MSTR", "ELF", "CROX", "CVNA", "UPST", "AI", "IONQ", "JOBY", "QS", "SPCE", "OPEN", "GME", "AMC", "TLRY", "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES", "COP", "EOG", "VLO", "MPC", "PSX", "KMI", "WMB", "ET", "EPD", "MPLX", "PAA", "VNOM", "OIH", "XOP", "USO", "UNG", "BOIL", "KOLD", "GUSH", "NUGT", "DUST", "JNUG", "LIT", "URA", "REMX", "COPX", "SLX", "FAN", "GRID", "BATT", "DRIV", "KARS", "HAIL", "IDRV", "VCAR", "UWMC", "RKT", "LDI", "PFSI", "GHIV", "IVR", "MFA", "NYMT", "MITT", "TWO", "ARR", "CIM", "EARN", "ORC", "AGNC", "NLY", "STWD", "BXMT", "ABR", "RC", "GPMT", "KREF", "LADR", "TRTX", "ACRE", "ARI", "XAN", "CLNC", "HMG", "HASI", "SAFE", "STAR", "GTY", "NNN", "O", "WPC", "STAG", "ADC", "EPR", "VICI", "GLPI", "MGP", "IRT", "MAA", "CPT", "ESS", "AVB", "EQR", "UDR", "AIV", "INVH", "AMH", "TCON", "UMH", "SUI", "ELS", "CUBE", "EXR", "PSA", "LSI", "NSA", "COLD", "DLR", "EQIX", "COR", "CONE", "QTS", "AMT", "CCI", "SBAC", "UNIT", "LAMR", "OUT", "WY", "PCH", "RYN", "CTT", "LAND", "FPI", "AGM"]
}

# ==============================================================================
# 2. MOTOR DE ANÁLISIS
# ==============================================================================
def analizar(ticker, interval, strategy):
    try:
        df = yf.download(ticker, period="3y", interval=interval, progress=False)
        if df is None or len(df) < 30: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9']
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch['STOCHk_14_3_3']

        curr = df.iloc[-1]
        
        if strategy == "Oportunidades Premium (Fusión)":
            # Lógica v22 para detectar señales tipo CUBE
            m_bull = (curr['MACD'] > 0) and (curr['K'] < 30)
            m_bear = (curr['MACD'] < 0) and (curr['K'] > 70)
            if m_bull:
                return {"Ticker": f"**{ticker}**", "Señal": "<span class='prem-buy'>🚀 BUY PREMIUM</span>", "Velas": "Actual", "Stoch": round(curr['K'],1), "Precio": round(float(curr['Close']), 2)}
            if m_bear:
                return {"Ticker": f"**{ticker}**", "Señal": "<span class='prem-sell'>💀 SELL PREMIUM</span>", "Velas": "Actual", "Stoch": round(curr['K'],1), "Precio": round(float(curr['Close']), 2)}

        elif strategy == "Velas de Cambio (Barrido)":
            for i in range(1, 9):
                c, p = df.iloc[-i], df.iloc[-(i+1)]
                mid = (p['High'] + p['Low']) / 2
                sig = ""
                if c['Low'] < p['Low'] and c['Close'] > mid and c['K'] < 30: sig = "<span class='sig-up'>ALCISTA 🟢</span>"
                elif c['High'] > p['High'] and c['Close'] < mid and c['K'] > 70: sig = "<span class='sig-down'>BAJISTA 🔴</span>"
                if sig:
                    return {"Ticker": f"**{ticker}**", "Señal": sig, "Velas": f"Hace {i-1}", "Stoch": round(c['K'],1), "Precio": round(float(c['Close']), 2)}

        return None
    except: return None

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================
st.title("🦅 GEMA FUSIÓN v49 PRO")
st.caption("CENTER COMMAND | INDUSTRIAL ASSETS SCANNER")

c1, c2, c3 = st.columns(3)
with c1:
    idx = st.selectbox("📁 Índice Escogido:", list(universos.keys()))
    activos = universos[idx]
with c2:
    temp = st.radio("⏱️ Temporalidad:", ["Semanal", "Mensual"], horizontal=True)
    inter = "1wk" if temp == "Semanal" else "1mo"
with c3:
    estrat = st.selectbox("🧠 Inteligencia:", ["Oportunidades Premium (Fusión)", "Velas de Cambio (Barrido)"])

st.markdown(f"📡 **OBJETIVOS CARGADOS:** {len(activos)} activos en radar.")

if st.button("🔥 LANZAR RADAR DE ALTA INTENSIDAD"):
    encontrados = []
    prog = st.progress(0)
    status = st.empty()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(analizar, t, inter, estrat): t for t in activos}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ticker)):
            t = future_to_ticker[future]
            status.markdown(f"⏳ **Escaneando {i+1} de {len(activos)}:** `{t}`")
            res = future.result()
            if res: encontrados.append(res)
            prog.progress((i+1)/len(activos))
            
    status.markdown(f"### ✅ BARRIDO COMPLETADO. SE HAN DETECTADO {len(encontrados)} OPORTUNIDADES.")
    
    if encontrados:
        st.balloons()
        df_res = pd.DataFrame(encontrados)
        # Mostramos la tabla con fondo blanco usando HTML
        st.write(df_res.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.download_button("📥 EXPORTAR CSV", df_res.to_csv(index=False).encode('utf-8'), f"gema_{idx}.csv")
    else:
        st.info("Sin señales claras. Mantener liquidez.")

st.sidebar.divider()
st.sidebar.info("Modo de tabla blanca activado. Motor de 20 hilos para escaneo masivo de índices completos.")
