
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. Configuración básica
st.set_page_config(page_title="Gema Radar", layout="wide")
st.title("🎯 Radar Barrido v35")

# 2. Lista de activos (Simplificada para probar)
activos = ["AAPL", "MSFT", "NVDA", "TSLA", "BTC-USD", "ETH-USD", "GC=F", "ITX.MC", "SAN.MC"]

# 3. Función de análisis
def analizar(ticker):
    try:
        # Descarga datos semanales
        df = yf.download(ticker, period="1y", interval="1wk", progress=False)
        if df.empty: return None
        
        # Limpieza de columnas (Evita el error de yfinance)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Cálculo de indicadores
        df['MACD'] = ta.macd(df['Close'])['MACD_12_26_9']
        df['K'] = ta.stoch(df['High'], df['Low'], df['Close'])['STOCHk_14_3_3']
        
        # Lógica de Barrido (Engaño)
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        mid_prev = (prev['High'] + prev['Low']) / 2
        
        # Detectar señal
        if curr['Low'] < prev['Low'] and curr['Close'] > mid_prev:
            return "ALCISTA 🟢", round(curr['K'], 1)
        if curr['High'] > prev['High'] and curr['Close'] < mid_prev:
            return "BAJISTA 🔴", round(curr['K'], 1)
            
        return None, round(curr['K'], 1)
    except Exception as e:
        return f"Error: {e}", 0

# 4. Interfaz
if st.button("🚀 LANZAR ESCÁNER"):
    resultados = []
    for t in activos:
        st.write(f"Analizando {t}...")
        senal, stoch = analizar(t)
        if senal:
            resultados.append({"Ticker": t, "Señal": senal, "Estocástico": stoch})
    
    if resultados:
        st.table(resultados)
    else:
        st.success("Escaneo terminado. Sin señales claras ahora.")
