import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA INFINITE v39", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050a12; color: #e0e0e0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        color: black; font-weight: bold; border-radius: 20px; border: none;
        box-shadow: 0 0 15px #4facfe; height: 3em;
    }
    .metric-card {
        background-color: #1a1e26; padding: 15px; border-radius: 10px;
        border-left: 5px solid #00f2fe; margin-bottom: 10px;
    }
    .signal-up { color: #00ff88; font-weight: bold; }
    .signal-down { color: #ff3344; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🏎️ GEMA MACDELOREAN v39.0 - Infinite Edition")

# --- LAS MEGA LISTAS (MÁXIMA POTENCIA) ---
listas = {
    "🇺🇸 NASDAQ TOP 25": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AMD", "NFLX", "AVGO", "COST", "ADBE", "TXN", "INTU", "QCOM", "AMAT", "SBUX", "ISRG", "MDLZ", "GILD", "INTC", "ADP", "VRTX", "REGN", "ADI"],
    "🇪🇸 IBEX 35 (FULL)": ["ITX.MC", "SAN.MC", "BBVA.MC", "TEF.MC", "IBE.MC", "REP.MC", "CABK.MC", "ACS.MC", "GRF.MC", "ANA.MC", "AMS.MC", "AENA.MC", "BKT.MC", "ELE.MC", "ENG.MC", "FDR.MC", "IAG.MC", "IDR.MC", "MAP.MC", "MRL.MC", "SCYR.MC", "UNI.MC", "ROVI.MC"],
    "🇺🇸 S&P 500 ELITE": ["JPM", "V", "MA", "PG", "HD", "CVX", "KO", "DIS", "WMT", "UNH", "CAT", "BA", "XOM", "BAC", "LLY", "ABBV", "PFE", "TMO", "COST", "MCD", "NKE", "LIN", "PM", "GS", "HON"],
    "🇩🇪 DAX 40": ["SAP.DE", "SIE.DE", "DTE.DE", "ALV.DE", "AIR.DE", "BMW.DE", "BAS.DE", "VOW3.DE", "DBK.DE", "BAYN.DE", "IFX.DE", "CON.DE", "HEI.DE", "MUV2.DE", "RWE.DE"],
    "🇺🇸 DOW JONES": ["AXP", "AMGN", "AAPL", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"],
    "🇺🇸 RUSSELL 2000": ["IWM", "UNIT", "SRCE", "GCO", "BKE", "AMRK", "PLXS", "SAIA", "ENSG", "MEDP", "KNSL", "FIX", "ELF", "IBP", "LGIH"],
    "₿ CRIPTOS / COMMOS": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "DOT-USD", "LINK-USD", "GC=F", "CL=F", "SI=F", "HG=F", "NG=F"]
}

# --- INTERFAZ DE USUARIO ---
col_t, col_s = st.columns([1, 1])
with col_t:
    temp = st.radio("⏱️ Temporalidad:", ["Semanal", "Mensual"], horizontal=True)
    intervalo = "1wk" if temp == "Semanal" else "1mo"

with col_s:
    st.write("### 🛡️ Escuadrones Activos:")
    seleccionados = []
    # Usamos columnas pequeñas para que los checkboxes no ocupen tanto espacio
    c1, c2 = st.columns(2)
    for i, (cat, ticks) in enumerate(listas.items()):
        target_col = c1 if i % 2 == 0 else c2
        if target_col.checkbox(cat, value=(i==0)):
            seleccionados.extend(ticks)

# Contador de activos
total = len(seleccionados)
st.markdown(f"""
    <div class="metric-card">
        <h4 style='margin:0;'>📊 ESTADO DEL SISTEMA</h4>
        <p style='font-size: 1.3rem; color: #00f2fe; margin:0;'>Listo para analizar <b>{total}</b> activos en <b>{temp}</b></p>
    </div>
""", unsafe_allow_html=True)

def analizar(ticker, interval):
    try:
        # Descarga un poco más de datos para asegurar el cálculo del MACD
        df = yf.download(ticker, period="3y", interval=interval, progress=False)
        if df is None or len(df) < 30: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicadores
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9']
        df['Hist'] = macd['MACDh_12_26_9']
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch['STOCHk_14_3_3']
        
        # Lógica Barrido (Últimas 6 velas)
        for i in range(1, 7):
            curr, prev = df.iloc[-i], df.iloc[-(i+1)]
            mid_prev = (prev['High'] + prev['Low']) / 2
            
            sig = ""
            if curr['Low'] < prev['Low'] and curr['Close'] > mid_prev: sig = "ALCISTA 🟢"
            elif curr['High'] > prev['High'] and curr['Close'] < mid_prev: sig = "BAJISTA 🔴"
            
            if sig:
                m_val = float(curr['MACD'])
                m_txt = f"<span class='signal-up'>ALCISTA (>{round(m_val,2)})</span>" if m_val > 0 else f"<span class='signal-down'>BAJISTA (<{round(m_val,2)})</span>"
                
                return {
                    "TICKER": f"**{ticker}**",
                    "SEÑAL": f"<span class='{'signal-up' if '🟢' in sig else 'signal-down'}'>{sig}</span>",
                    "VELAS ATRÁS": i-1,
                    "MACD (0)": m_txt,
                    "HIST. MACD": "⬆️ Subiendo" if curr['Hist'] > df.iloc[-(i+1)]['Hist'] else "⬇️ Bajando",
                    "ESTOCÁSTICO": f"{round(float(curr['K']), 1)}%",
                    "CIERRE": round(float(curr['Close']), 2)
                }
        return None
    except: return None

if st.button("⚡ INICIAR ESCANEO MASIVO"):
    if total == 0:
        st.error("Selecciona al menos un escuadrón, Capitán.")
    else:
        encontrados = []
        barra = st.progress(0)
        status = st.empty()
        
        for idx, t in enumerate(seleccionados):
            status.text(f"Analizando {t}... ({idx+1}/{total})")
            res = analizar(t, intervalo)
            if res: encontrados.append(res)
            barra.progress((idx+1)/total)
        
        status.text("✅ Escaneo Finalizado")
        
        if encontrados:
            st.balloons()
            df_final = pd.DataFrame(encontrados)
            st.write(df_final.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # Botón de descarga
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DESCARGAR PARA EXCEL", data=csv, file_name=f"gema_infinite_{temp}.csv")
        else:
            st.info("No se han detectado barridos en esta selección.")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/d/d8/DeLorean_DMC-12_front_right.jpg")
st.sidebar.markdown("---")
st.sidebar.write("**TIPS DEL RADAR:**")
st.sidebar.write("1. **SEMANAL:** Señales para swing trading (semanas).")
st.sidebar.write("2. **MENSUAL:** Señales de largo plazo (meses).")
st.sidebar.write("3. **HIST MACD:** Si sube, hay fuerza detrás del movimiento.")
