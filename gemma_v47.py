

import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Macdelorean Radar v23",
    page_icon="🦅",
    layout="wide"
)

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

    .stApp { background-color: #080c10; color: #c9d1d9; }

    h1, h2, h3 {
        color: #00e676 !important;
        font-family: 'Orbitron', monospace !important;
        letter-spacing: 2px;
    }

    /* Botón principal */
    div.stButton > button {
        width: 100%;
        border: 2px solid #00e676;
        background: linear-gradient(135deg, #0a1628 0%, #0d2137 100%);
        color: #00e676;
        font-weight: bold;
        font-size: 18px;
        padding: 14px;
        font-family: 'Orbitron', monospace;
        letter-spacing: 3px;
        transition: all 0.3s;
        text-transform: uppercase;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #00e676 0%, #00bcd4 100%);
        color: #000000;
        box-shadow: 0 0 20px #00e676aa;
    }

    /* Checkboxes */
    .stCheckbox label { color: #00e676 !important; font-family: 'Share Tech Mono', monospace; font-size: 14px; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #0d1117; border-bottom: 1px solid #00e676; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-family: 'Orbitron', monospace; font-size: 12px; }
    .stTabs [aria-selected="true"] { color: #00e676 !important; border-bottom: 2px solid #00e676; }

    /* Progress bar */
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #00e676, #00bcd4); }

    /* Métricas */
    div[data-testid="stMetricValue"] { font-size: 1.4rem; color: #ffffff; font-family: 'Share Tech Mono', monospace; }
    div[data-testid="stMetricLabel"] { color: #8b949e; font-family: 'Share Tech Mono', monospace; }

    /* Dataframe */
    .stDataFrame { border: 1px solid #1e3a2f; }

    /* Info/warning/success */
    .stAlert { border-left: 4px solid #00e676; background-color: #0d1117; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #1e3a2f; }
    section[data-testid="stSidebar"] h2 { font-size: 14px !important; }

    /* Divider */
    hr { border-color: #1e3a2f; }

    /* Expander */
    .streamlit-expanderHeader { color: #00e676 !important; font-family: 'Share Tech Mono', monospace; }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 1. UNIVERSO DE ACTIVOS ORGANIZADO POR ÍNDICE
# ==============================================================================

UNIVERSO = {
    "🇺🇸 DOW JONES 30": [
        "MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS",
        "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK",
        "MSFT", "NKE", "PG", "CRM", "TRV", "UNH", "VZ", "V", "WMT", "AMZN"
    ],

    "🚀 NASDAQ 100": [
        "NVDA", "META", "TSLA", "AVGO", "PEP", "COST", "TMUS", "ADBE", "TXN",
        "CMCSA", "AMD", "NFLX", "QCOM", "BKNG", "ADI", "MDLZ", "ADP", "ISRG",
        "REGN", "VRTX", "PYPL", "LRCX", "FISV", "CSX", "MU", "MELI", "AMAT",
        "PANW", "SNPS", "CDNS", "ORLY", "ASML", "KLAC", "MAR", "FTNT", "CHTR",
        "CTAS", "NXPI", "DXCM", "LULU", "PCAR", "BIIB", "IDXX", "MCHP", "ROST",
        "PAYX", "EA", "CTSH", "FAST", "DLTR", "WDAY", "VRSK", "ODFL", "BKR",
        "CEG", "DDOG", "ZS", "CRWD", "TEAM", "ON", "GEHC", "AZN", "TTWO",
        "MNST", "SBUX", "PDD", "JD", "BIDU", "ZM", "EBAY", "ALGN", "ENPH"
    ],

    "📈 S&P 500 SELECT": [
        "LLY", "XOM", "UNH", "MA", "BAC", "LIN", "DHR", "NEE", "PM", "RTX",
        "GE", "UBER", "ABNB", "PLTR", "BRK-B", "SPGI", "BLK", "SCHW", "CB",
        "CI", "MO", "DUK", "SO", "D", "EXC", "SRE", "AEP", "XEL", "ED",
        "WEC", "ES", "ETR", "CNP", "CMS", "LNT", "PNW", "OGE", "NI", "EVRG",
        "MDT", "ABT", "TMO", "BMY", "GILD", "AMGN", "SYK", "EW", "DXCM",
        "ZBH", "BDX", "RMD", "HOLX", "PKI", "WAT", "IQV", "CTLT", "MTD",
        "A", "BAX", "BSX", "COO", "HSIC", "ICE", "NDAQ", "CME", "CBOE",
        "AON", "MMC", "AJG", "WTW", "HIG", "MET", "PRU", "GL", "LNC",
        "UNM", "PFG", "TROW", "BEN", "IVZ", "AMG", "VRTS", "SEIC", "APAM"
    ],

    "🇩🇪 DAX 40": [
        "SAP.DE", "SIE.DE", "AIR.DE", "ALV.DE", "DTE.DE", "MBG.DE", "VOW3.DE",
        "BMW.DE", "BAS.DE", "ADS.DE", "IFX.DE", "DHL.DE", "MUV2.DE", "DB1.DE",
        "BEI.DE", "RWE.DE", "EOAN.DE", "SY1.DE", "BAYN.DE", "DTG.DE", "HEN3.DE",
        "VNA.DE", "CON.DE", "PAH3.DE", "MTX.DE", "HEI.DE", "MRK.DE", "BNR.DE",
        "HNR1.DE", "ZAL.DE", "FRE.DE", "FME.DE", "QIA.DE", "PUM.DE", "SHL.DE",
        "ENR.DE", "EVT.DE", "1COV.DE", "SON22.DE", "SXS.DE"
    ],

    "🇪🇸 IBEX 35": [
        "ITX.MC", "IBE.MC", "BBVA.MC", "SAN.MC", "CABK.MC", "TEF.MC", "ACS.MC",
        "FER.MC", "AENA.MC", "AMS.MC", "REP.MC", "CLNX.MC", "IAG.MC", "ENG.MC",
        "ANA.MC", "GRF.MC", "RED.MC", "MTS.MC", "ACX.MC", "BKT.MC", "MAP.MC",
        "TL5.MC", "MEL.MC", "PHM.MC", "SAB.MC", "IDR.MC", "COL.MC", "LOG.MC",
        "FDR.MC", "ROVI.MC", "SOL.MC", "UNI.MC", "VIS.MC", "ELE.MC", "CIE.MC"
    ],

    "🇫🇷 CAC 40": [
        "MC.PA", "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA", "AIR.PA", "SU.PA",
        "BNP.PA", "SAF.PA", "EL.PA", "AXA.PA", "DG.PA", "KER.PA", "DSY.PA",
        "STLAP.PA", "RI.PA", "CAP.PA", "GLE.PA", "ORA.PA", "BN.PA", "EN.PA",
        "LR.PA", "ACA.PA", "CA.PA", "ML.PA", "VIE.PA", "SGO.PA", "HO.PA",
        "ATO.PA", "PUB.PA", "WLN.PA", "URW.PA", "RNO.PA", "VIV.PA", "ENGI.PA",
        "STM.PA", "TEP.PA", "BOL.PA", "ERF.PA", "AF.PA"
    ],

    "🇬🇧 FTSE 100": [
        "SHEL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L", "GSK.L", "RIO.L",
        "DGE.L", "BHP.L", "REL.L", "NG.L", "BATS.L", "VOD.L", "LLOY.L",
        "NWG.L", "BARC.L", "PRU.L", "LGEN.L", "AV.L", "STAN.L", "ABF.L",
        "ANTO.L", "AUTO.L", "AVV.L", "BA.L", "BNZL.L", "BT-A.L", "CCH.L",
        "CPG.L", "CNA.L", "CRDA.L", "DCC.L", "DPH.L", "EZJ.L", "FERG.L",
        "FLTR.L", "GLEN.L", "HLMA.L", "HL.L", "IHG.L", "IMB.L", "INF.L",
        "ITV.L", "JD.L", "KGF.L", "LAND.L", "MNG.L", "MRO.L", "NXT.L",
        "OCDO.L", "PSN.L", "PSON.L", "RKT.L", "RR.L", "RS1.L", "SGE.L",
        "SMDS.L", "SMIN.L", "SKG.L", "SPX.L", "SSE.L", "SBRY.L", "SVT.L",
        "TSCO.L", "TUI.L", "UU.L", "WPP.L", "WTB.L"
    ],

    "⚡ ETFs & SECTORES": [
        "XLK", "XLF", "XLV", "XLE", "XLC", "XLY", "XLP", "XLI", "XLB", "XLRE", "XLU",
        "QQQ", "SPY", "IWM", "DIA", "VTI", "EWZ", "EEM", "GDX", "GDXJ",
        "SMH", "SOXX", "XBI", "KWEB", "TAN", "ICLN", "LIT", "URA",
        "GLD", "SLV", "USO", "UNG", "CORN", "WEAT", "SOYB",
        "TLT", "IEF", "HYG", "LQD", "BNDX",
        "MSTR", "COIN", "MARA", "RIOT", "CLSK"
    ],

    "🎯 SMALL CAPS & ESPECULATIVOS": [
        "SOFI", "AFRM", "HOOD", "DKNG", "LCID", "RIVN", "PLTR",
        "CRWD", "DDOG", "ZS", "NET", "SNOW", "OKTA", "TWLO", "BILL",
        "UPST", "AI", "IONQ", "JOBY", "QS", "OPEN",
        "GME", "AMC", "BBBY", "TLRY", "SNDL", "ACB",
        "CVNA", "CROX", "ELF", "CELH", "HIMS", "ACMR",
        "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES",
        "VLO", "MPC", "PSX", "FANG", "EOG", "COP",
        "KMI", "WMB", "ET", "EPD", "MPLX"
    ]
}


# ==============================================================================
# 2. INTELIGENCIA TÉCNICA
# ==============================================================================

def procesar_datos(ticker):
    try:
        df_d = yf.download(ticker, period="1y",  interval="1d",  progress=False, auto_adjust=True)
        df_w = yf.download(ticker, period="3y",  interval="1wk", progress=False, auto_adjust=True)
        df_m = yf.download(ticker, period="5y",  interval="1mo", progress=False, auto_adjust=True)

        if df_d.empty or df_w.empty or df_m.empty:
            return None

        # Fix MultiIndex de yfinance
        if isinstance(df_d.columns, pd.MultiIndex): df_d = df_d.xs(ticker, axis=1, level=1)
        if isinstance(df_w.columns, pd.MultiIndex): df_w = df_w.xs(ticker, axis=1, level=1)
        if isinstance(df_m.columns, pd.MultiIndex): df_m = df_m.xs(ticker, axis=1, level=1)

        for df in [df_d, df_w, df_m]:
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            if macd is not None:
                df['MACD']   = macd['MACD_12_26_9']
                df['Signal'] = macd['MACDs_12_26_9']
            if len(df) > 15:
                stoch = df.ta.stoch(k=14, d=3)
                if stoch is not None:
                    df['K'] = stoch['STOCHk_14_3_3']

        return {'D': df_d, 'W': df_w, 'M': df_m}
    except:
        return None


# ---- VELA DE ENGAÑO ----
def check_vela_engano(df, idx=-1):
    if len(df) < abs(idx) + 2 or 'K' not in df.columns:
        return False, "", 0, 0

    curr = df.iloc[idx]
    prev = df.iloc[idx - 1]
    mid_prev = (prev['High'] + prev['Low']) / 2
    k = curr['K']

    if (curr['Low'] < prev['Low']) and (curr['Close'] > mid_prev) and (k < 20.0):
        return True, "ALCISTA 🟢", k, min(curr['Low'], prev['Low'])
    if (curr['High'] > prev['High']) and (curr['Close'] < mid_prev) and (k > 80.0):
        return True, "BAJISTA 🔴", k, max(curr['High'], prev['High'])
    return False, "", k, 0


# ---- DIVERGENCIAS MACD ----
def check_divergencia(df, ventana=10):
    """
    Divergencia alcista: precio hace mínimo más bajo pero MACD hace mínimo más alto.
    Divergencia bajista: precio hace máximo más alto pero MACD hace máximo más bajo.
    """
    if 'MACD' not in df.columns or len(df) < ventana + 2:
        return False, ""

    recent = df.iloc[-ventana:]

    # Divergencia ALCISTA
    idx_min_price = recent['Close'].idxmin()
    idx_min_macd  = recent['MACD'].idxmin()
    pos_price = recent.index.get_loc(idx_min_price)
    pos_macd  = recent.index.get_loc(idx_min_macd)

    price_at_min_macd = recent['Close'].iloc[pos_macd]
    macd_at_min_price = recent['MACD'].iloc[pos_price]

    if (recent['Close'].iloc[-1] < price_at_min_macd) and (recent['MACD'].iloc[-1] > macd_at_min_price):
        return True, "DIV ALCISTA 📈"

    # Divergencia BAJISTA
    idx_max_price = recent['Close'].idxmax()
    idx_max_macd  = recent['MACD'].idxmax()
    pos_price_max = recent.index.get_loc(idx_max_price)
    pos_macd_max  = recent.index.get_loc(idx_max_macd)

    price_at_max_macd = recent['Close'].iloc[pos_macd_max]
    macd_at_max_price = recent['MACD'].iloc[pos_price_max]

    if (recent['Close'].iloc[-1] > price_at_max_macd) and (recent['MACD'].iloc[-1] < macd_at_max_price):
        return True, "DIV BAJISTA 📉"

    return False, ""


# ---- OPERACIONES PREMIUM (M+W+D confluencia) ----
def super_buscador(pack):
    m = pack['M']; w = pack['W']; d = pack['D']
    if 'MACD' not in m.columns or len(m) < 2:
        return False, "", 0

    curr_m = m.iloc[-1]; prev_m = m.iloc[-2]
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
# 3. INTERFAZ
# ==============================================================================

st.markdown("""
<div style='text-align:center; padding: 10px 0 5px 0;'>
    <span style='font-family: Orbitron, monospace; font-size: 2.2rem; font-weight: 900;
                 color: #00e676; letter-spacing: 6px; text-shadow: 0 0 20px #00e676aa;'>
        🦅 MACDELOREAN v23
    </span><br>
    <span style='font-family: Share Tech Mono, monospace; font-size: 0.85rem;
                 color: #8b949e; letter-spacing: 4px;'>
        SISTEMA DE INTELIGENCIA ESTRUCTURAL MULTI-ÍNDICE
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# SIDEBAR - PANEL DE CONTROL
# ==============================================================================
with st.sidebar:
    st.markdown("## 🎛️ PANEL DE CONTROL")
    st.markdown("---")

    # --- SELECCIÓN DE ÍNDICES ---
    st.markdown("### 📊 ÍNDICES A ESCANEAR")
    indices_seleccionados = []
    for nombre_indice in UNIVERSO.keys():
        n_tickers = len(UNIVERSO[nombre_indice])
        if st.checkbox(f"{nombre_indice} ({n_tickers})", value=True, key=f"idx_{nombre_indice}"):
            indices_seleccionados.append(nombre_indice)

    st.markdown("---")

    # --- FILTROS DE BÚSQUEDA ---
    st.markdown("### 🔍 FILTROS DE BÚSQUEDA")
    filtro_premium   = st.checkbox("💎 Operaciones Premium (M+W+D)", value=True)
    filtro_velas     = st.checkbox("🕯️ Velas de Engaño (W/M)",       value=True)
    filtro_diverg    = st.checkbox("📐 Divergencias MACD",            value=False)

    st.markdown("---")

    # --- FILTRO DIRECCIÓN ---
    st.markdown("### 🧭 DIRECCIÓN")
    dir_alcista = st.checkbox("🟢 Mostrar señales ALCISTAS", value=True)
    dir_bajista = st.checkbox("🔴 Mostrar señales BAJISTAS", value=True)

    st.markdown("---")

    # --- RESUMEN ---
    total_tickers = sum(len(UNIVERSO[i]) for i in indices_seleccionados)
    st.markdown(f"""
    <div style='background:#0d2137; border:1px solid #00e676; border-radius:6px; padding:10px; text-align:center;'>
        <span style='font-family:Share Tech Mono; color:#8b949e; font-size:12px;'>OBJETIVOS SELECCIONADOS</span><br>
        <span style='font-family:Orbitron; color:#00e676; font-size:2rem; font-weight:700;'>{total_tickers}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    lanzar = st.button("🔥 LANZAR RADAR")

# ==============================================================================
# LÓGICA DE EJECUCIÓN
# ==============================================================================
if lanzar:
    if not indices_seleccionados:
        st.error("⚠️ Selecciona al menos un índice en el panel lateral.")
        st.stop()

    if not (filtro_premium or filtro_velas or filtro_diverg):
        st.error("⚠️ Activa al menos un filtro de búsqueda.")
        st.stop()

    # Construir lista de tickers únicos
    master_list = []
    for idx_name in indices_seleccionados:
        master_list.extend(UNIVERSO[idx_name])
    master_list = list(dict.fromkeys(master_list))  # quitar duplicados manteniendo orden

    st.success(f"📡 CONECTANDO CON **{len(master_list)} OBJETIVOS** EN **{len(indices_seleccionados)} ÍNDICES**. ESCANEO EN PROCESO...")

    res_prem  = []
    res_velas = []
    res_diverg = []

    progress_bar = st.progress(0)
    status_text  = st.empty()
    col_live1, col_live2, col_live3 = st.columns(3)
    ph_prem  = col_live1.empty()
    ph_velas = col_live2.empty()
    ph_div   = col_live3.empty()

    for i, ticker in enumerate(master_list):
        progress_bar.progress((i + 1) / len(master_list))
        status_text.text(f"🔎 Analizando: {ticker}  [{i+1}/{len(master_list)}]")
        time.sleep(0.05)

        pack = procesar_datos(ticker)
        if pack is None:
            continue

        precio = round(float(pack['D'].iloc[-1]['Close']), 2)

        # ---- PREMIUM ----
        if filtro_premium:
            es_sup, txt, stop = super_buscador(pack)
            if es_sup:
                if ("BUY" in txt and dir_alcista) or ("SELL" in txt and dir_bajista):
                    res_prem.append({
                        "Ticker":    ticker,
                        "Señal":     txt,
                        "Precio":    precio,
                        "Stop Ref":  round(float(stop), 2)
                    })
                    ph_prem.dataframe(pd.DataFrame(res_prem), use_container_width=True)

        # ---- VELAS DE ENGAÑO ----
        if filtro_velas:
            for tf_key, tf_name in [('M', 'MENSUAL'), ('W', 'SEMANAL')]:
                for j in range(4):
                    es, t, k, s = check_vela_engano(pack[tf_key], idx=-1-j)
                    if es:
                        es_alc = "ALCISTA" in t
                        if (es_alc and dir_alcista) or (not es_alc and dir_bajista):
                            res_velas.append({
                                "Ticker":     ticker,
                                "TF":         tf_name,
                                "Señal":      t,
                                "Antigüedad": f"Hace {j} {'Mes' if tf_key=='M' else 'Sem'}",
                                "Stoch K":    round(k, 1),
                                "Precio":     precio
                            })
                            ph_velas.dataframe(pd.DataFrame(res_velas), use_container_width=True)
                        break

        # ---- DIVERGENCIAS ----
        if filtro_diverg:
            for tf_key, tf_name in [('D', 'DIARIO'), ('W', 'SEMANAL'), ('M', 'MENSUAL')]:
                es_div, tipo_div = check_divergencia(pack[tf_key], ventana=10)
                if es_div:
                    es_alc_div = "ALCISTA" in tipo_div
                    if (es_alc_div and dir_alcista) or (not es_alc_div and dir_bajista):
                        res_diverg.append({
                            "Ticker":  ticker,
                            "TF":      tf_name,
                            "Tipo":    tipo_div,
                            "Precio":  precio
                        })
                        ph_div.dataframe(pd.DataFrame(res_diverg), use_container_width=True)

    # Limpiar placeholders temporales
    ph_prem.empty(); ph_velas.empty(); ph_div.empty()
    progress_bar.empty()
    status_text.success("✅ ESCANEO COMPLETADO.")
    st.balloons()

    # --- RESUMEN EJECUTIVO ---
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 Tickers Escaneados", len(master_list))
    m2.metric("💎 Señales Premium",    len(res_prem))
    m3.metric("🕯️ Velas Engaño",      len(res_velas))
    m4.metric("📐 Divergencias",       len(res_diverg))
    st.markdown("---")

    # --- TABS RESULTADOS ---
    num_tabs = sum([filtro_premium, filtro_velas, filtro_diverg])
    tab_labels = []
    if filtro_premium: tab_labels.append(f"💎 PREMIUM ({len(res_prem)})")
    if filtro_velas:   tab_labels.append(f"🕯️ VELAS ENGAÑO ({len(res_velas)})")
    if filtro_diverg:  tab_labels.append(f"📐 DIVERGENCIAS ({len(res_diverg)})")

    tabs = st.tabs(tab_labels)
    tab_idx = 0

    if filtro_premium:
        with tabs[tab_idx]:
            if res_prem:
                df_out = pd.DataFrame(res_prem)
                st.dataframe(df_out, use_container_width=True)
                csv = df_out.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Exportar CSV", csv, "premium.csv", "text/csv")
            else:
                st.warning("El mercado no ofrece entradas Premium hoy. Mantener disciplina.")
        tab_idx += 1

    if filtro_velas:
        with tabs[tab_idx]:
            if res_velas:
                df_out = pd.DataFrame(res_velas)
                # Separar alcistas / bajistas
                alc = df_out[df_out['Señal'].str.contains("ALCISTA")]
                baj = df_out[df_out['Señal'].str.contains("BAJISTA")]
                if not alc.empty:
                    st.markdown("#### 🟢 ALCISTAS")
                    st.dataframe(alc, use_container_width=True)
                if not baj.empty:
                    st.markdown("#### 🔴 BAJISTAS")
                    st.dataframe(baj, use_container_width=True)
                csv = df_out.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Exportar CSV", csv, "velas.csv", "text/csv")
            else:
                st.info("No se han detectado velas de engaño extremas.")
        tab_idx += 1

    if filtro_diverg:
        with tabs[tab_idx]:
            if res_diverg:
                df_out = pd.DataFrame(res_diverg)
                alc = df_out[df_out['Tipo'].str.contains("ALCISTA")]
                baj = df_out[df_out['Tipo'].str.contains("BAJISTA")]
                if not alc.empty:
                    st.markdown("#### 📈 DIVERGENCIAS ALCISTAS")
                    st.dataframe(alc, use_container_width=True)
                if not baj.empty:
                    st.markdown("#### 📉 DIVERGENCIAS BAJISTAS")
                    st.dataframe(baj, use_container_width=True)
                csv = df_out.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Exportar CSV", csv, "divergencias.csv", "text/csv")
            else:
                st.info("No se han detectado divergencias en los parámetros seleccionados.")

else:
    # --- PANTALLA INICIAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style='background:#0d1117; border:1px solid #1e3a2f; border-radius:8px; padding:16px;'>
            <div style='font-family:Orbitron; color:#00e676; font-size:13px; margin-bottom:8px;'>📊 ÍNDICES DISPONIBLES</div>
            <div style='font-family:Share Tech Mono; color:#8b949e; font-size:12px; line-height:1.8;'>
                🇺🇸 DOW JONES 30<br>
                🚀 NASDAQ 100<br>
                📈 S&P 500 SELECT<br>
                🇩🇪 DAX 40<br>
                🇪🇸 IBEX 35<br>
                🇫🇷 CAC 40<br>
                🇬🇧 FTSE 100<br>
                ⚡ ETFs & SECTORES<br>
                🎯 SMALL CAPS
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style='background:#0d1117; border:1px solid #1e3a2f; border-radius:8px; padding:16px;'>
            <div style='font-family:Orbitron; color:#00e676; font-size:13px; margin-bottom:8px;'>🔍 FILTROS ACTIVOS</div>
            <div style='font-family:Share Tech Mono; color:#8b949e; font-size:12px; line-height:1.8;'>
                💎 Operaciones Premium<br>&nbsp;&nbsp;&nbsp;→ Confluencia M + W + D<br>
                🕯️ Velas de Engaño<br>&nbsp;&nbsp;&nbsp;→ Barrido + Estocástico<br>
                📐 Divergencias MACD<br>&nbsp;&nbsp;&nbsp;→ Precio vs Momentum
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style='background:#0d1117; border:1px solid #1e3a2f; border-radius:8px; padding:16px;'>
            <div style='font-family:Orbitron; color:#00e676; font-size:13px; margin-bottom:8px;'>⚙️ LÓGICA DE SEÑALES</div>
            <div style='font-family:Share Tech Mono; color:#8b949e; font-size:12px; line-height:1.8;'>
                PREMIUM: MACD Mensual<br>&nbsp;&nbsp;&nbsp;+ Correctivo Semanal<br>&nbsp;&nbsp;&nbsp;+ Giro Diario<br>&nbsp;&nbsp;&nbsp;+ Vela Engaño<br><br>
                DIVERGENCIA: Precio ↕<br>&nbsp;&nbsp;&nbsp;vs MACD ↕ (10 velas)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; font-family:Share Tech Mono; color:#3d4f3d; font-size:13px; letter-spacing:3px;'>
        ← SELECCIONA ÍNDICES Y FILTROS EN EL PANEL IZQUIERDO · PULSA LANZAR RADAR →
    </div>
    """, unsafe_allow_html=True)





