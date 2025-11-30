import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Macdelorean Radar v22",
    page_icon="🦅",
    layout="wide"
)

# --- ESTILOS VISUALES (MODO GUERRA) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Courier New', monospace; }
    div.stButton > button { 
        width: 100%; 
        border: 1px solid #00e676; 
        background-color: #161b22; 
        color: #00e676; 
        font-weight: bold; 
        font-size: 16px;
        padding: 10px;
    }
    div.stButton > button:hover { 
        background-color: #00e676; 
        color: #000000; 
        border-color: #00e676; 
    }
    .stProgress > div > div > div > div { background-color: #00e676; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. LISTAS DE ACTIVOS (HARDCODED PARA MÓVIL)
# ==============================================================================
@st.cache_data
def get_universe(mode_slow):
    # DOW JONES 30
    dow = ["MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS", "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PG", "CRM", "TRV", "UNH", "VZ", "V", "WMT", "AMZN"]
    
    # SECTORES
    sect = ["XLK", "XLF", "XLV", "XLE", "XLC", "XLY", "XLP", "XLI", "XLB", "XLRE", "XLU"]
    
    # NASDAQ & SP500 SELECT (Líquidos)
    tech = ["NVDA", "META", "TSLA", "AVGO", "PEP", "COST", "TMUS", "ADBE", "TXN", "CMCSA", "AMD", "NFLX", "QCOM", "BKNG", "ADI", "MDLZ", "ADP", "ISRG", "REGN", "VRTX", "PYPL", "LRCX", "FISV", "CSX", "MU", "MELI", "AMAT", "KDP", "PANW", "SNPS", "MNST", "CDNS", "ORLY", "ASML", "KLAC", "MAR", "FTNT", "CHTR", "CTAS", "NXPI", "DXCM", "LULU", "EXC", "PCAR", "KHC", "AEP", "BIIB", "IDXX", "MCHP", "ROST", "PAYX", "EA", "CTSH", "FAST", "DLTR", "WDAY", "VRSK", "ODFL", "BKR", "CEG", "DDOG", "ZS", "CRWD", "TEAM", "LCID", "RIVN", "PDD", "JD", "BIDU", "SIRI", "ZM", "EBAY", "ALGN", "ENPH", "BRK-B", "LLY", "XOM", "UNH", "MA", "BAC", "WMT", "LIN", "DHR", "NEE", "PM", "RTX", "GE", "UBER", "ABNB", "PLTR", "SOFI", "AFRM", "HOOD", "DKNG", "MARA", "RIOT", "CLSK", "COIN"]
    
    # EUROPA
    euro = ["ITX.MC", "IBE.MC", "BBVA.MC", "SAN.MC", "CABK.MC", "TEF.MC", "ACS.MC", "FER.MC", "AENA.MC", "AMS.MC", "REP.MC", "CLNX.MC", "IAG.MC", "ENG.MC", "ANA.MC", "GRF.MC", "RED.MC", "MTS.MC", "ACX.MC", "BKT.MC", "MAP.MC", "TL5.MC", "MEL.MC", "PHM.MC", "SAB.MC", "IDR.MC", "COL.MC", "LOG.MC", "FDR.MC", "ROVI.MC", "SOL.MC", "UNI.MC", "VIS.MC", "ELE.MC", "SAP.DE", "SIE.DE", "AIR.DE", "ALV.DE", "DTE.DE", "MBG.DE", "VOW3.DE", "BMW.DE", "BAS.DE", "ADS.DE", "IFX.DE", "DHL.DE", "MUV2.DE", "DB1.DE", "BEI.DE", "RWE.DE", "EOAN.DE", "SY1.DE", "BAYN.DE", "DTG.DE", "HEN3.DE", "VNA.DE", "CON.DE", "PAH3.DE", "MTX.DE", "HEI.DE", "LIN.DE", "MRK.DE", "BNR.DE", "HNR1.DE", "ZAL.DE", "FRE.DE", "FME.DE", "QIA.DE", "PUM.DE", "SHL.DE", "MC.PA", "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA", "AIR.PA", "SU.PA", "BNP.PA", "SAF.PA", "EL.PA", "AXA.PA", "DG.PA", "KER.PA", "DSY.PA", "STLAP.PA", "RI.PA", "CAP.PA", "GLE.PA", "ORA.PA", "BN.PA", "EN.PA", "LR.PA", "ACA.PA", "CA.PA", "ML.PA", "VIE.PA", "SGO.PA", "HO.PA", "ATO.PA", "PUB.PA", "WLN.PA", "URW.PA", "RNO.PA", "VIV.PA", "ENGI.PA"]
    
    # RUSSELL (Selección)
    russell = ["IWM", "TNA", "URTY", "SMH", "SOXX", "XBI", "KWEB", "EWZ", "EEM", "GDX", "GDXJ", "SIL", "TAN", "ICLN", "PBW", "MSTR", "ELF", "CROX", "CVNA", "UPST", "AI", "IONQ", "JOBY", "QS", "SPCE", "OPEN", "NKLA", "SAVA", "GME", "AMC", "TLRY", "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES", "COP", "EOG", "PXD", "FANG", "VLO", "MPC", "PSX", "KMI", "WMB", "ET", "EPD", "MPLX", "PAA", "VNOM", "OIH", "XOP", "AMLP", "USO", "UNG", "BOIL", "KOLD", "GUSH", "DRIP", "ERX", "ERY", "NUGT", "DUST", "JNUG", "JDST", "LIT", "URA", "REMX", "COPX", "SLX", "FAN", "GRID", "BATT", "DRIV", "KARS", "HAIL", "IDRV", "VCAR", "FUV", "SOLO", "WKHS", "RIDE", "GOEV", "HYLN", "XL", "UWMC", "RKT", "LDI", "PFSI", "GHIV", "IVR", "MFA", "NYMT", "MITT", "TWO", "ARR", "CIM", "EARN", "ORC", "AGNC", "NLY", "STWD", "BXMT", "ABR", "RC", "GPMT", "KREF", "LADR", "TRTX", "ACRE", "ARI", "XAN", "CLNC", "HMG", "HASI", "SAFE", "STAR", "GTY", "NNN", "O", "WPC", "STAG", "ADC", "EPR", "VICI", "GLPI", "MGP", "IRT", "MAA", "CPT", "ESS", "AVB", "EQR", "UDR", "AIV", "INVH", "AMH", "TCON", "UMH", "SUI", "ELS", "CUBE", "EXR", "PSA", "LSI", "NSA", "COLD", "DLR", "EQIX", "COR", "CONE", "QTS", "AMT", "CCI", "SBAC", "UNIT", "LAMR", "OUT", "WY", "PCH", "RYN", "CTT", "LAND", "FPI", "AGM"]

    full_list = list(set(dow + sect + tech + euro + russell))
    return full_list

# ==============================================================================
# 2. INTELIGENCIA TÉCNICA
# ==============================================================================
def procesar_datos(ticker):
    try:
        # Descarga con reintentos para móvil
        df_d = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        df_w = yf.download(ticker, period="3y", interval="1wk", progress=False, auto_adjust=True)
        df_m = yf.download(ticker, period="5y", interval="1mo", progress=False, auto_adjust=True)
        
        if df_d.empty or df_w.empty or df_m.empty: return None

        # Fix MultiIndex
        if isinstance(df_d.columns, pd.MultiIndex): df_d = df_d.xs(ticker, axis=1, level=1)
        if isinstance(df_w.columns, pd.MultiIndex): df_w = df_w.xs(ticker, axis=1, level=1)
        if isinstance(df_m.columns, pd.MultiIndex): df_m = df_m.xs(ticker, axis=1, level=1)
        
        for df in [df_d, df_w, df_m]:
            # MACD
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            if macd is not None:
                df['MACD'] = macd['MACD_12_26_9'] 
                df['Signal'] = macd['MACDs_12_26_9']
            # Stoch
            if len(df) > 15:
                stoch = df.ta.stoch(k=14, d=3)
                if stoch is not None: df['K'] = stoch['STOCHk_14_3_3']
                
        return {'D': df_d, 'W': df_w, 'M': df_m}
    except: return None

def check_vela_engano(df, idx=-1):
    if len(df) < abs(idx)+2 or 'K' not in df.columns: return False, "", 0, 0
    curr = df.iloc[idx]; prev = df.iloc[idx-1]
    
    mid_prev = (prev['High'] + prev['Low']) / 2
    l_curr = curr['Low']; h_curr = curr['High']; c_curr = curr['Close']; k = curr['K']
    l_prev = prev['Low']; h_prev = prev['High']
    
    # COMPRA
    if (l_curr < l_prev) and (c_curr > mid_prev) and (k < 20.0):
        return True, "ALCISTA 🟢", k, min(l_curr, l_prev)
    # VENTA
    if (h_curr > h_prev) and (c_curr < mid_prev) and (k > 80.0):
        return True, "BAJISTA 🔴", k, max(h_curr, h_prev)
    return False, "", k, 0

def super_buscador(pack):
    """ M>0/Inclinado + W Correctivo + D Giro + Vela Engaño """
    m = pack['M']; w = pack['W']; d = pack['D']
    if 'MACD' not in m.columns: return False, "", 0
    if len(m) < 2: return False, "", 0
    
    curr_m = m.iloc[-1]; prev_m = m.iloc[-2]
    # Mensual Estricto
    m_bull = (curr_m['MACD'] > 0) and (curr_m['MACD'] > curr_m['Signal']) and (curr_m['MACD'] > prev_m['MACD'])
    m_bear = (curr_m['MACD'] < 0) and (curr_m['MACD'] < curr_m['Signal']) and (curr_m['MACD'] < prev_m['MACD'])
    
    w_curr = w.iloc[-1]; d_curr = d.iloc[-1]
    
    for i in range(5):
        idx = -1 - i
        es_vela, tipo, k, stop = check_vela_engano(w, idx=idx)
        
        if m_bull and (w_curr['MACD'] < w_curr['Signal']) and (d_curr['MACD'] > d_curr['Signal']) and es_vela and "ALCISTA" in tipo:
            return True, f"💎 BUY PREMIUM (Hace {i} sem)", stop
        if m_bear and (w_curr['MACD'] > w_curr['Signal']) and (d_curr['MACD'] < d_curr['Signal']) and es_vela and "BAJISTA" in tipo:
            return True, f"💀 SELL PREMIUM (Hace {i} sem)", stop
            
    return False, "", 0

# ==============================================================================
# 3. INTERFAZ VISUAL
# ==============================================================================

# Header Táctico
st.title("🦅 MACDELOREAN v22")
st.caption("SISTEMA DE INTELIGENCIA ESTRUCTURAL | CLEAN CUT")

# Panel de Control
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("### 🎛️ Mando")
    scan_mode = st.radio("Intensidad de Escaneo:", ["Total War (Todos los Activos)"])
    if st.button("🔥 LANZAR RADAR"):
        run_scan = True
    else:
        run_scan = False

with col2:
    st.markdown("### 📊 Reglas de Combate")
    c1, c2, c3 = st.columns(3)
    c1.metric("MACD Mensual", "Estricto", "Sin Cruces")
    c2.metric("Vela Engaño", "Barrido", "> 50% Recup")
    c3.metric("Divergencias", "OFF", "Desactivadas")

st.markdown("---")

# Lógica de Ejecución
if run_scan:
    master_list = get_universe(scan_mode)
    st.success(f"📡 CONECTANDO CON {len(master_list)} OBJETIVOS. ESCANEO EN PROCESO...")
    
    res_prem, res_vela = [], []
    
    # Barra de Progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Contenedor de Resultados en tiempo real
    placeholder_prem = st.empty()
    
    for i, ticker in enumerate(master_list):
        progress_bar.progress((i + 1) / len(master_list))
        status_text.text(f"Analizando: {ticker}...")
        
        # Pausa mínima para que Yahoo no bloquee en la nube
        time.sleep(0.05) 
        
        pack = procesar_datos(ticker)
        if pack is None: continue
        
        precio = round(pack['D'].iloc[-1]['Close'], 2)
        
        # 1. PREMIUM
        es_sup, txt, stop = super_buscador(pack)
        if es_sup: 
            res_prem.append({"Ticker": ticker, "Señal": txt, "Precio": precio, "Stop Loss Ref": round(stop, 2)})
            # Mostrar hallazgo inmediato
            placeholder_prem.dataframe(pd.DataFrame(res_prem))
            
        # 2. VELAS (W/M)
        for j in range(4):
            idx = -1 - j
            es, t, k, s = check_vela_engano(pack['M'], idx)
            if es:
                res_vela.append({"Ticker": ticker, "TF": "MENSUAL", "Señal": t, "Antigüedad": f"Hace {j} Mes", "Stoch": round(k,1), "Precio": precio})
                break
        for j in range(4):
            idx = -1 - j
            es, t, k, s = check_vela_engano(pack['W'], idx)
            if es:
                res_vela.append({"Ticker": ticker, "TF": "SEMANAL", "Señal": t, "Antigüedad": f"Hace {j} Sem", "Stoch": round(k,1), "Precio": precio})
                break

    st.balloons()
    status_text.text("✅ ESCANEO COMPLETADO.")
    
    # Visualización Final
    tab1, tab2 = st.tabs(["💎 OPORTUNIDADES PREMIUM", "🕯️ VELAS DE ENGAÑO"])
    
    with tab1:
        if res_prem:
            st.dataframe(pd.DataFrame(res_prem), use_container_width=True)
        else:
            st.warning("El mercado no ofrece entradas Premium hoy. Mantener disciplina.")
            
    with tab2:
        if res_vela:
            st.dataframe(pd.DataFrame(res_vela), use_container_width=True)
        else:
            st.info("No se han detectado velas de engaño extremas.")

else:
    st.info("👈 Pulsa 'LANZAR RADAR' para iniciar el barrido masivo.")

