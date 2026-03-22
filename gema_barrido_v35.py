
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Gema Radar", layout="wide")
st.title("🎯 Radar Barrido v35")

# Lista de activos
activos = ["AAPL", "MSFT", "NVDA", "TSLA", "BTC-USD", "ETH-USD", "GC=F", "ITX.MC", "SAN.MC"]

def analizar(ticker):
    try:
        # Descarga
        df = yf.download(ticker, period="1y", interval="1wk", progress=False)
        if df is None or len(df) < 10:
            return "Sin datos", 0
        
        # Limpieza para nuevas versiones de pandas/yfinance
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Indicadores
        macd_data = ta.macd(df['Close'])
        df['MACD'] = macd_data['MACD_12_26_9']
        stoch_data = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch_data['STOCHk_14_3_3']
        
        # Lógica
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        mid_prev = (prev['High'] + prev['Low']) / 2
        
        res = "Nada"
        if curr['Low'] < prev['Low'] and curr['Close'] > mid_prev:
            res = "ALCISTA 🟢"
        elif curr['High'] > prev['High'] and curr['Close'] < mid_prev:
            res = "BAJISTA 🔴"
            
        return res, round(float(curr['K']), 1)
    except Exception as e:
        return f"Error", 0

if st.button("🚀 LANZAR ESCÁNER"):
    resultados = []
    for t in activos:
        st.write(f"Analizando {t}...")
        # Aquí estaba el fallo, ahora está protegido:
        resultado_analisis = analizar(t)
        senal, stoch = resultado_analisis
        
        if senal != "Nada" and senal != "Error" and senal != "Sin datos":
            resultados.append({"Ticker": t, "Señal": senal, "Estocástico": stoch})
    
    if resultados:
        st.table(resultados)
    else:
        st.info("Escaneo terminado. No hay señales de barrido en estos activos hoy.")
