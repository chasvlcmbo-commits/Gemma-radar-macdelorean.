import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GEMA v37 - GLOBAL RADAR", layout="wide")

st.markdown("""
    <style>
    .main { background: #0e1117; color: white; }
    .stButton>button { width: 100%; background: #00ff00; color: black; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 GEMA MACDELOREAN v37 - Global Radar")

# --- SELECTOR DE TEMPORALIDAD ---
temp = st.radio("⏱️ Selecciona Temporalidad de Análisis:", ["Semanal", "Mensual"], horizontal=True)
intervalo = "1wk" if temp == "Semanal" else "1mo"

# --- EL GRAN EJÉRCITO (LISTAS AMPLIADAS) ---
listas = {
    "🇺🇸 NASDAQ 100": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AMD", "NFLX", "AVGO", "COST", "PYPL"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "TEF.MC", "IBE.MC", "REP.MC", "CABK.MC", "ACS.MC", "GRF.MC"],
    "🇩🇪 DAX 40": ["SAP.DE", "SIE.DE", "DTE.DE", "ALV.DE", "AIR.DE", "BMW.DE", "BAS.DE"],
    "🇺🇸 S&P 500 / DOW": ["JPM", "V", "PG", "HD", "CVX", "KO", "DIS", "INTC", "WMT", "UNH"],
    "🇺🇸 RUSSELL 2000": ["IWM", "UNIT", "SRCE", "GCO", "BKE", "AMRK"],
    "₿ CRIPTOS / ORO": ["BTC-USD", "ETH-USD", "SOL-USD", "GC=F", "CL=F"]
}

def analizar(ticker, period="2y", interval="1wk"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or len(df) < 20: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicadores
        macd = ta.macd(df['Close'])
        df['Hist'] = macd['MACDh_12_26_9']
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch['STOCHk_14_3_3']
        
        # Buscar en las últimas 6 velas
        for i in range(1, 7):
            curr, prev = df.iloc[-i], df.iloc[-(i+1)]
            mid_prev = (prev['High'] + prev['Low']) / 2
            
            sig = "Nada"
            if curr['Low'] < prev['Low'] and curr['Close'] > mid_prev: sig = "ALCISTA 🟢"
            elif curr['High'] > prev['High'] and curr['Close'] < mid_prev: sig = "BAJISTA 🔴"
            
            if sig != "Nada":
                return {
                    "Ticker": ticker,
                    "Señal": sig,
                    "Hace (Velas)": i-1,
                    "Estocástico": f"{round(float(curr['K']), 1)}%",
                    "MACD Hist": "⬆️" if curr['Hist'] > df.iloc[-(i+1)]['Hist'] else "⬇️",
                    "Cierre": round(float(curr['Close']), 2)
                }
        return None
    except: return None

# --- INTERFAZ ---
st.write("### 🛡️ Escuadrones a escanear:")
cols = st.columns(len(listas))
seleccion = []
for i, (nombre, ticks) in enumerate(listas.items()):
    if cols[i].checkbox(nombre, value=(i<2)): seleccion.extend(ticks)

if st.button(f"🚀 INICIAR BARRIDO {temp.upper()}"):
    encontrados = []
    prog = st.progress(0)
    for i, t in enumerate(seleccion):
        res = analizar(t, interval=intervalo)
        if res: encontrados.append(res)
        prog.progress((i+1)/len(seleccion))
    
    if encontrados:
        df_final = pd.DataFrame(encontrados)
        st.table(df_final)
        
        # --- BOTÓN DE EXCEL (CSV) ---
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Resultados para Excel", data=csv, file_name=f"barrido_{temp}.csv", mime='text/csv')
    else:
        st.warning("No se detectaron señales.")
