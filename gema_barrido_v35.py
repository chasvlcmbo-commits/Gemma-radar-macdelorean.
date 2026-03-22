
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="GEMA DASHBOARD v36", layout="wide")

# Estilo CSS Avanzado para Dark Mode y Tablas Premium
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; color: white; }
    .main { background: #0e1117; color: white; }
    h1, h2, h3, h4, h5, h6 { color: white !important; }
    .stCheckbox>label { color: #d1d1d1 !important; font-size: 1.1rem; }
    .stButton>button { width: 100%; background: linear-gradient(135deg, #00ff00 0%, #009900 100%); color: black !important; font-weight: bold; border: none; padding: 10px; border-radius: 8px; font-size: 1.1rem; cursor: pointer; }
    .stButton>button:hover { background: linear-gradient(135deg, #33ff33 0%, #00cc00 100%); }
    .stTable { background-color: #1a1e26; color: white; border-radius: 10px; border: 1px solid #333; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .stTable thead tr th { background-color: #0e1117; color: #d1d1d1 !important; font-weight: bold; border-bottom: 2px solid #333; }
    .stTable tbody tr td { border-bottom: 1px solid #333; font-size: 1rem; }
    .stTable tbody tr:hover { background-color: #262c38; }
    
    /* Colores para las celdas */
    .signal-up { color: #00ff00; font-weight: bold; }
    .signal-down { color: #ff3333; font-weight: bold; }
    .macd-up { color: #88ff88; font-weight: bold; }
    .macd-down { color: #ff8888; font-weight: bold; }
    .neutral { color: #aaaaaa; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 GEMA MACDELOREAN v36.0 - Dashboard Semanal")
st.subheader("Buscando Barridos de Liquidez Semanales y Confirmación de Momentum")

# --- DICCIONARIO DE ACTIVOS (EL EJÉRCITO COMPLETO) ---
activos_full = {
    "🇺🇸 NASDAQ 100 (TOP)": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "AMD", "NFLX", "COST", "AVGO", "PYPL"],
    "🇺🇸 DOW JONES": ["JNJ", "V", "PG", "HD", "CVX", "MRK", "KO", "DIS", "INTC"],
    "🇪🇸 IBEX 35": ["ITX.MC", "SAN.MC", "BBVA.MC", "TEF.MC", "IBE.MC", "REP.MC", "CABK.MC", "ACS.MC", "FER.MC"],
    "🇬🇧 FTSE 100": ["HSBA.L", "BP.L", "VOD.L", "GSK.L", "AZN.L", "BA.L"],
    "₿ CRIPTOS / COMMODITIES": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "GC=F", "CL=F", "HG=F", "ZC=F"]
}

# --- FUNCIÓN DE ANÁLISIS MEJORADA (HISTÓRICO) ---
def analizar_historico(ticker):
    try:
        # Descarga datos semanales (necesitamos un periodo mayor para el histórico)
        df = yf.download(ticker, period="2y", interval="1wk", progress=False)
        if df is None or len(df) < 52: return None # Al menos un año de datos
        
        # Limpieza de MultiIndex
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # INDICADORES (MACD, Histograma, Estocástico)
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9']
        df['Hist'] = macd['MACDh_12_26_9']
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['K'] = stoch['STOCHk_14_3_3']
        
        # --- LÓGICA DE BARRIDO ---
        def es_barrido(current, previous):
            mid_prev = (previous['High'] + previous['Low']) / 2
            # Barrido Alcista
            if current['Low'] < previous['Low'] and current['Close'] > mid_prev:
                return "ALCISTA 🟢"
            # Barrido Bajista
            elif current['High'] > previous['High'] and current['Close'] < mid_prev:
                return "BAJISTA 🔴"
            return "Nada"

        # --- BUSCAR SEÑAL ACTIVA Y HACE CUÁNTAS SEMANAS ---
        # Miramos las últimas 8 semanas (2 meses aprox)
        looking_back_weeks = 8
        found_signal = "Nada"
        weeks_ago = 0
        
        for i in range(1, looking_back_weeks + 1):
            curr = df.iloc[-i]
            prev = df.iloc[-(i+1)]
            signal = es_barrido(curr, prev)
            
            if signal != "Nada":
                found_signal = signal
                weeks_ago = i - 1
                break # Encontramos la más reciente y paramos
        
        # --- DATOS DEL MACD ACTUAL ---
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        macd_semillas = ""
        # Semilla del MACD Linea (Cruce)
        if curr['MACD'] > 0 and prev['MACD'] <= 0: macd_semillas += "LINEA ⬆️ "
        elif curr['MACD'] < 0 and prev['MACD'] >= 0: macd_semillas += "LINEA ⬇️ "
        
        # Semilla del Histograma (Momentum)
        if curr['Hist'] > prev['Hist']: macd_semillas += "HIST ⬆️"
        else: macd_semillas += "HIST ⬇️"
        
        if found_signal != "Nada":
            weeks_str = "Hoy" if weeks_ago == 0 else f"{weeks_ago} sem"
            return {
                "ACTIVO": f"**{ticker}**",
                "SEÑAL BARRIDO": f"<span class='{'signal-up' if '🟢' in found_signal else 'signal-down'}'>{found_signal}</span>",
                "HACE CUÁNTO": f"<span class='neutral'>{weeks_str}</span>",
                "ESTOCÁSTICO": f"<span class='{'signal-down' if float(curr['K']) > 80 else 'signal-up' if float(curr['K']) < 20 else 'neutral'}'>{round(float(curr['K']), 1)}%</span>",
                "MARCADOR MACD": f"<span class='{'macd-up' if curr['Hist'] > prev['Hist'] else 'macd-down'}'>{macd_semillas}</span>",
                "CIERRE ACT.": f"${round(float(curr['Close']), 2)}"
            }
        return None
    except:
        return None

# --- INTERFAZ ---
st.write("---")
# Selectores de activos en columnas
st.write("### 🛡️ Selecciona tu Ejército:")
cols_sel = st.columns(len(activos_full))
seleccionados = []
for i, (cat, lista) in enumerate(activos_full.items()):
    with cols_sel[i]:
        if st.checkbox(cat, value=True if i < 3 else False):
            seleccionados.extend(lista)

if st.button("🚀 INICIAR BARRIDO PROFESIONAL"):
    st.divider()
    with st.spinner("Escaneando el mercado... el Delorean está acelerando."):
        encontrados = []
        progreso = st.progress(0)
        
        for index, ticker in enumerate(seleccionados):
            res = analizar_historico(ticker)
            if res:
                encontrados.append(res)
            progreso.progress((index + 1) / len(seleccionados))
        
        if encontrados:
            st.balloons()
            # Convertimos los dicts a un DataFrame para aplicarle el renderizado HTML
            df_encontrados = pd.DataFrame(encontrados)
            # Renderizamos la tabla con HTML permitido para los colores
            st.write(df_encontrados.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.write("---")
            st.info("Nota: GEMA Dashboard v36 busca señales activas en las últimas 8 semanas (gráfico semanal).")
        else:
            st.warning("No se han encontrado barridos de liquidez claros en las últimas semanas.")

# --- SIDEBAR DE INFORMACIÓN ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/29/DeLorean_DMC-12_on_highway_%28cropped%29.jpg", width=200)
    st.title("GEMA v36")
    st.info("Sistema de trading algorítmico basado en trampas de mercado y momentum semanal.")
    st.write("---")
    st.write("**Glosario:**")
    st.write("- **🟢 ALCISTA:** Barrido de mínimos anterior con cierre en media superior.")
    st.write("- **🔴 BAJISTA:** Barrido de máximos anterior con cierre en media inferior.")
    st.write("- **LINEA ⬆️ / ⬇️:** Cruce de la línea MACD por encima/debajo de cero.")
    st.write("- **HIST ⬆️ / ⬇️:** Momentum del histograma MACD subiendo/bajando.")
