import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import concurrent.futures
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA v55 NISON SNIPER", page_icon="🦅", layout="wide")

# --- ESTILOS VISUALES (Tablas Blancas y Modo Guerra) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Courier New', monospace; }
    
    div.stButton > button { 
        width: 100%; border: 2px solid #00e676; background-color: #161b22; 
        color: #00e676; font-weight: bold; font-size: 18px; padding: 12px;
        border-radius: 8px; box-shadow: 0 0 10px rgba(0,230,118,0.2);
    }
    
    /* TABLA BLANCA PROFESIONAL */
    .rendered_html table {
        background-color: white !important;
        color: #1c1c1c !important;
        border-radius: 8px;
        width: 100%;
        border: 1px solid #dee2e6 !important;
    }
    .rendered_html th {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        font-weight: bold;
        padding: 12px !important;
        border: 1px solid #dee2e6 !important;
        text-transform: uppercase;
    }
    .rendered_html td {
        color: #1c1c1c !important;
        padding: 10px !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 500;
    }
    
    .sig-up { color: #1a7f37; font-weight: bold; }
    .sig-down { color: #d1242f; font-weight: bold; }
    .prem-buy { color: #1a7f37; font-weight: 900; background-color: #e6ffec; padding: 4px; border-radius: 4px; }
    .prem-sell { color: #d1242f; font-weight: 900; background-color: #ffebe9; padding: 4px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. EL ARSENAL TOTAL (PROTEGIENDO TODOS LOS TICKERS)
# ==============================================================================
universos = {
    "🇺🇸 S&P 500 (FULL)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "TSLA", "UNH", "LLY", "JPM", "XOM", "V", "MA", "PG", "AVGO", "HD", "CVX", "ABBV", "KO", "MRK", "PEP", "COST", "TMO", "MCD", "ADBE", "WMT", "CSCO", "CRM", "PFE", "BAC", "ACN", "ABT", "LIN", "NFLX", "ORCL", "AMD", "TXN", "PM", "INTC", "VZ", "HON", "DIS", "T", "UPS", "NEE", "BMY", "LOW", "SPGI", "RTX", "CAT", "AMGN", "GE", "IBM", "UNP", "GS", "INTU", "DE", "PLD", "AXP", "MS", "ELV", "GILD", "SYK", "AMT", "LMT", "BLK", "MDLZ", "CVS", "BKNG", "ISRG", "ADI", "ADP", "TJX", "MMC", "VRTX", "CI", "REGN", "ZTS", "BSX", "CUBE", "BKR", "ADSK", "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMAT", "AMCR", "AMP", "AMT", "AON", "APA", "APD", "APH", "APTV", "ARE", "ATO", "AVB", "AVY", "AWK", "AXON", "AYI", "AZO", "BA", "BALL", "BBWI", "BBY", "BDX", "BEN", "BF-B", "BG", "BIIB", "BIO", "BK", "BKR", "BLDR", "BLK", "BMY", "BR", "BRO", "BSX", "BWA", "BX", "BXP", "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCL", "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CI", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "COST", "CPB", "CPRT", "CPT", "CRL", "CRM", "CSGP", "CSL", "CSX", "CTAS", "CTLT", "CTRA", "CTSH", "CTVA", "CVS", "CVX", "CZR", "D", "DAL", "DAN", "DD", "DE", "DFS", "DG", "DGX", "DHI", "DHR", "DISH", "DLR", "DLTR", "DOCU", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "ELV", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN", "ETR", "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FCX", "FDS", "FDX", "FE", "FFIV", "FI", "FICO", "FIS", "FITB", "FLT", "FMC", "FOX", "FOXA", "FRT", "FSLR", "FTNT", "FTV", "GD", "GE", "GEHC", "GEN", "GILD", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC", "GPN", "GRMN", "GS", "GWRE", "GWW", "HAL", "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUM", "HWM", "IBM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INDV", "INTC", "INTU", "INVH", "IP", "IPG", "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KDP", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LULU", "LUV", "LVS", "LW", "LYB", "LYV", "MA", "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "METP", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", "MO", "MOH", "MOS", "MPC", "MPWR", "MRK", "MRNA", "MS", "MSCI", "MSFT", "MSI", "MTB", "MTCH", "MTD", "MU", "NCLH", "NDAQ", "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWS", "NWSA", "NXPI", "O", "ODFL", "OKE", "OMC", "ON", "ORCL", "ORLY", "OTIS", "OXY", "PANW", "PARA", "PAYC", "PAYX", "PCAR", "PCG", "PEAK", "PEG", "PEP", "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PLD", "PM", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PXD", "PYPL", "QCOM", "QRVO", "RCL", "RE", "REG", "REGN", "RF", "RHI", "RJF", "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "RVTY", "SBAC", "SBUX", "SCHW", "SHW", "SIER", "SIVB", "SJM", "SLB", "SNA", "SNPS", "SO", "SPG", "SPGI", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGT", "TJX", "TMO", "TMUS", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXN", "TXT", "TYL", "UAL", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB", "V", "VFC", "VICI", "VLO", "VMC", "VNO", "VRSK", "VRSN", "VRTX", "VTR", "VTRS", "VZ", "WAB", "WAT", "WBA", "WBD", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WMT", "WRB", "WRK", "WST", "WTW", "WY", "WYNN", "XEL", "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZTS"],
    "🇺🇸 NASDAQ 100": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "ADBE", "NFLX", "AMD", "QCOM", "TXN", "INTU", "AMAT", "ISRG", "BKNG", "HON", "MU", "ADI", "ADP", "LRCX", "VRTX", "REGN", "PANW", "SNPS", "KLAC", "CDNS", "MELI", "MAR", "ORLY", "CTAS", "ASML", "CSX", "PYPL", "MNST", "FTNT", "KDP", "LULU", "WDAY", "ADSK", "NXPI", "EXC", "PCAR", "ROST", "PAYX", "EA", "CTSH", "FAST", "DLTR", "VRSK", "ODFL", "BKR", "CEG", "DDOG", "ZS", "CRWD", "TEAM", "MSTR", "PDD", "EBAY", "JD", "BIDU", "SIRI", "ZM", "ALGN", "ENPH"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "IBE.MC", "TEF.MC", "REP.MC", "CABK.MC", "ACS.MC", "FER.MC", "AENA.MC", "AMS.MC", "ANA.MC", "BKT.MC", "CLNX.MC", "ELE.MC", "ENG.MC", "FDR.MC", "GRF.MC", "IAG.MC", "IDR.MC", "MAP.MC", "MRL.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "UNI.MC", "VIS.MC", "MEL.MC", "SAB.MC", "LOG.MC", "COL.MC"],
    "🇩🇪 DAX 40 (DE)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "VOW3.DE", "MUV2.DE", "DHL.DE", "DBK.DE", "EOAN.DE", "RWE.DE", "IFX.DE", "BAYN.DE", "HEI.DE", "CON.DE", "MRK.DE", "BEI.DE", "ADS.DE", "DB1.DE", "SY1.DE", "VNA.DE", "DTG.DE", "HEN3.DE", "PAH3.DE", "MTX.DE", "LIN.DE", "BNR.DE", "ZAL.DE", "FRE.DE", "FME.DE", "QIA.DE", "PUM.DE", "SHL.DE"],
    "🇫🇷 CAC 40 (FR)": ["MC.PA", "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA", "AIR.PA", "BNP.PA", "SU.PA", "EL.PA", "DG.PA", "AI.PA", "BN.PA", "CS.PA", "KER.PA", "VIV.PA", "ENGI.PA", "CAP.PA", "ML.PA", "ACA.PA", "CA.PA", "SAF.PA", "AXA.PA", "DSY.PA", "STLAP.PA", "RI.PA", "GLE.PA", "ORA.PA", "EN.PA", "LR.PA", "VIE.PA", "SGO.PA", "HO.PA", "ATO.PA", "PUB.PA", "WLN.PA", "URW.PA", "RNO.PA"],
    "🇮🇹 FTSE MIB (IT)": ["RACE.MI", "ENI.MI", "ISP.MI", "UCG.MI", "STLAM.MI", "G.MI", "EGP.MI", "PRY.MI", "ENEL.MI", "TEN.MI", "AZM.MI", "FBK.MI", "A2A.MI", "AMP.MI", "BAMI.MI", "BPER.MI", "CPR.MI", "DIA.MI", "ERG.MI", "INW.MI", "LDO.MI", "MB.MI", "MONC.MI", "PIRC.MI", "PST.MI", "REC.MI", "SFER.MI", "SRG.MI", "STMMI.MI", "TIT.MI", "TRN.MI"],
    "🚜 RUSSELL 2000": ["IWM", "TNA", "URTY", "SMH", "SOXX", "XBI", "KWEB", "EWZ", "GDX", "MSTR", "ELF", "CROX", "CVNA", "UPST", "AI", "IONQ", "JOBY", "QS", "SPCE", "OPEN", "GME", "AMC", "TLRY", "OXY", "HAL", "SLB", "APA", "DVN", "MRO", "HES", "COP", "EOG", "VLO", "MPC", "PSX", "KMI", "WMB", "ET", "EPD", "MPLX", "PAA", "VNOM", "OIH", "XOP", "USO", "UNG", "BOIL", "KOLD", "GUSH", "NUGT", "DUST", "JNUG", "LIT", "URA", "REMX", "COPX", "SLX", "FAN", "GRID", "BATT", "DRIV", "KARS", "HAIL", "IDRV", "VCAR", "UWMC", "RKT", "LDI", "PFSI", "GHIV", "IVR", "MFA", "NYMT", "MITT", "TWO", "ARR", "CIM", "EARN", "ORC", "AGNC", "NLY", "STWD", "BXMT", "ABR", "RC", "GPMT", "KREF", "LADR", "TRTX", "ACRE", "ARI", "XAN", "CLNC", "HMG", "HASI", "SAFE", "STAR", "GTY", "NNN", "O", "WPC", "STAG", "ADC", "EPR", "VICI", "GLPI", "MGP", "IRT", "MAA", "CPT", "ESS", "AVB", "EQR", "UDR", "AIV", "INVH", "AMH", "TCON", "UMH", "SUI", "ELS", "CUBE", "EXR", "PSA", "LSI", "NSA", "COLD", "DLR", "EQIX", "COR", "CONE", "QTS", "AMT", "CCI", "SBAC", "UNIT", "LAMR", "OUT", "WY", "PCH", "RYN", "CTT", "LAND", "FPI", "AGM"]
}

# ==============================================================================
# 2. MOTOR DE ANÁLISIS (LÓGICA NISON SNIPER)
# ==============================================================================
def analizar(ticker, interval, strategy):
    try:
        df = yf.download(ticker, period="3y", interval=interval, progress=False)
        if df is None or len(df) < 30: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        # Indicadores
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9']
        df['Signal'] = macd['MACDs_12_26_9']
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch['STOCHk_14_3_3']

        for i in range(1, 6):
            c = df.iloc[-i]      # Vela actual
            p = df.iloc[-(i+1)]  # Vela anterior
            
            # --- LÓGICA DE VELAS JAPONESAS (Libro Nison) ---
            # El "Cuerpo" es el espacio entre Open y Close
            mid_cuerpo_p = (p['Open'] + p['Close']) / 2
            
            # 🟢 ALCISTA: Martillo / Envolvente / Piercing
            # 1. Barrido: Mínimo actual < Mínimo anterior
            # 2. Nison: Cierre actual > Mitad del cuerpo anterior
            es_nison_alcista = (c['Low'] < p['Low']) and (c['Close'] > mid_cuerpo_p) and (c['Close'] > c['Open'])

            # 🔴 BAJISTA: Estrella Fugaz / Nube Oscura
            # 1. Barrido: Máximo actual > Máximo anterior
            # 2. Nison: Cierre actual < Mitad del cuerpo anterior
            es_nison_bajista = (c['High'] > p['High']) and (c['Close'] < mid_cuerpo_p) and (c['Close'] < c['Open'])

            if strategy == "Oportunidades Premium (Sniper)":
                # Triple confluencia: Patrón Nison + Estocástico Agotado + MACD a favor
                if es_nison_alcista and c['K'] < 30 and c['MACD'] > c['Signal']:
                    return {"Ticker": f"**{ticker}**", "Señal": "<span class='prem-buy'>🚀 SNIPER BUY PREMIUM</span>", "Velas": f"Hace {i-1}", "MACD": "🟢 OK", "Stoch": round(c['K'],1), "Precio": round(float(c['Close']), 2)}
                
                if es_nison_bajista and c['K'] > 70 and c['MACD'] < c['Signal']:
                    return {"Ticker": f"**{ticker}**", "Señal": "<span class='prem-sell'>💀 SNIPER SELL PREMIUM</span>", "Velas": f"Hace {i-1}", "MACD": "🔴 OK", "Stoch": round(c['K'],1), "Precio": round(float(c['Close']), 2)}

            elif strategy == "Velas de Cambio (Barrido Simple)":
                if es_nison_alcista:
                    return {"Ticker": f"**{ticker}**", "Señal": "<span class='sig-up'>ALCISTA 🟢</span>", "Velas": f"Hace {i-1}", "Stoch": round(c['K'],1), "Precio": round(float(c['Close']), 2)}
                if es_nison_bajista:
                    return {"Ticker": f"**{ticker}**", "Señal": "<span class='sig-down'>BAJISTA 🔴</span>", "Velas": f"Hace {i-1}", "Stoch": round(c['K'],1), "Precio": round(float(c['Close']), 2)}

        return None
    except: return None

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================
st.title("🦅 GEMA FUSIÓN v55 NISON")
st.caption("TRIPLE FILTRO: BARRIDO + CIERRE NISON (50% CUERPO) + MACD")

c1, c2, c3 = st.columns(3)
with c1:
    idx = st.selectbox("📂 Selecciona el Ejército:", list(universos.keys()))
    activos = universos[idx]
with c2:
    temp = st.radio("⏱️ Temporalidad:", ["Semanal", "Mensual"], horizontal=True)
    inter = "1wk" if temp == "Semanal" else "1mo"
with c3:
    estrat = st.selectbox("🧠 Estrategia:", ["Oportunidades Premium (Sniper)", "Velas de Cambio (Barrido Simple)"])

st.markdown(f"📡 **OBJETIVOS IDENTIFICADOS:** {len(activos)} activos en lista.")

if st.button("🔥 LANZAR BARRIDO NISON"):
    encontrados = []
    prog = st.progress(0)
    status = st.empty()

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        future_to_ticker = {executor.submit(analizar, t, inter, estrat): t for t in activos}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ticker)):
            t = future_to_ticker[future]
            status.markdown(f"🎯 **Rastreando {i+1} de {len(activos)}:** `{t}`")
            res = future.result()
            if res: encontrados.append(res)
            prog.progress((i+1)/len(activos))

    status.markdown(f"### ✅ BARRIDO COMPLETADO.")

    if encontrados:
        st.balloons()
        df_res = pd.DataFrame(encontrados)
        st.write(df_res.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.download_button("📥 DESCARGAR CSV", df_res.to_csv(index=False).encode('utf-8'), f"gema_v55_{idx}.csv")
    else:
        st.info("Sin señales detectadas bajo los criterios de Nison hoy.")

st.sidebar.divider()
st.sidebar.info("Lógica Nison: Barrido + Cierre > 50% Cuerpo Anterior + Filtros Sniper.")




