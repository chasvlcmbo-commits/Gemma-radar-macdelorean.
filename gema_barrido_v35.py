
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA MACDELOREAN v35", layout="wide")

# Estilo personalizado: Fondo oscuro y tablas claras
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; background-color: #00ff00; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 GEMA MACDELOREAN v35.1 - Radar de Barrido")
st.subheader("Buscando barridos de liquidez en gráficos Semanales")

# --- DICCIONARIO DE ACTIVOS (EL EJÉRCITO) ---
activos = {
    "🇺🇸 NASDAQ / TOP": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AMD", "NFLX"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "TEF.MC", "IBE.MC", "REP.MC", "CABK.MC"],
    "₿ CRIPTOS / COMMODITIES": ["BTC-USD", "ETH-USD", "SOL-USD", "GC=F", "CL=F", "HG=F"]
}

def analizar(ticker):
    try:
        # Descarga datos semanales (1 año para tener contexto)
        df = yf.download(ticker, period="1y", interval="1wk", progress=False)
        if df is None or len(df) < 20: return None
        
        # Limpieza de MultiIndex
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # INDICADORES
        # MACD (Fuerza)
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9']
        df['Hist'] = macd['MACDh_12_26_9']
        
        # Estocástico (Sobreventa/Sobrecompra)
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch['STOCHk_14_3_3']
        
        # LÓGICA DE BARRIDO (The Macdelorean Logic)
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        mid_prev = (prev['High'] + prev['Low']) / 2
        
        signal = "Nada"
        color = "white"
        
        # BARRIDO ALCISTA: Mínimo actual menor al anterior + Cierre por encima del punto medio anterior
        if curr['Low'] < prev['Low'] and curr['Close'] > mid_prev:
            signal = "BARRIDO ALCISTA 🟢"
            # Filtro extra: Si el Histograma MACD está subiendo, es señal Triple A
            if curr['Hist'] > df.iloc[-2]['Hist']:
                signal = "BARRIDO ALCISTA (TOP) 🔥"
        
        # BARRIDO BAJISTA: Máximo actual mayor al anterior + Cierre por debajo del punto medio anterior
        elif curr['High'] > prev['High'] and curr['Close'] < mid_prev:
            signal = "BARRIDO BAJISTA 🔴"
            if curr['Hist'] < df.iloc[-2]['Hist']:
                signal = "BARRIDO BAJISTA (TOP) 💀"

        if signal != "Nada":
            return {
                "ACTIVO": ticker,
                "SEÑAL": signal,
                "ESTOCÁSTICO": f"{round(float(curr['K']), 1)}%",
                "CIERRE": f"{round(float(curr['Close']), 2)}",
                "MACD Hist": "⬆️" if curr['Hist'] > 0 else "⬇️"
            }
        return None
    except:
        return None

# --- INTERFAZ ---
cols = st.columns(len(activos))
seleccionados = []

for i, (cat, lista) in enumerate(activos.items()):
    with cols[i]:
        if st.checkbox(f"Seleccionar {cat}", value=True):
            seleccionados.extend(lista)

if st.button("🚀 INICIAR BARRIDO ESTRATÉGICO"):
    st.divider()
    encontrados = []
    
    progreso = st.progress(0)
    for index, ticker in enumerate(seleccionados):
        res = analizar(ticker)
        if res:
            encontrados.append(res)
        progreso.progress((index + 1) / len(seleccionados))
    
    if encontrados:
        st.balloons()
        st.table(encontrados)
    else:
        st.warning("No se han encontrado barridos de liquidez claros en esta selección.")

st.sidebar.info("Gema Macdelorean v35.1: Análisis basado en velas semanales para detectar trampas de mercado.")
