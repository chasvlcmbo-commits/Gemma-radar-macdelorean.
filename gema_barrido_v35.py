import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Gema Barrido v35", layout="wide")
st.title("🎯 Gema Macdelorean v35.0 - Barrido")

MERCADOS = {
    "DOW JONES": ["MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PG", "CRM", "TRV", "UNH", "VZ", "V", "WMT", "AMZN"],
    "NASDAQ & SP500": ["NVDA", "META", "TSLA", "AVGO", "PEP", "COST", "ADBE", "AMD", "NFLX", "QCOM", "PLTR", "MSTR", "UBER", "ABNB"],
    "IBEX & EUROPA": ["ITX.MC", "IBE.MC", "BBVA.MC", "SAN.MC", "CABK.MC", "TEF.MC", "SAB.MC", "BKT.MC", "SAP.DE", "SIE.DE", "MC.PA"],
    "CRYPTOS": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

def analizar_gema(ticker):
    try:
        df_w = yf.download(ticker, period="2y", interval="1wk", progress=False, auto_adjust=True)
        df_m = yf.download(ticker, period="5y", interval="1mo", progress=False, auto_adjust=True)
        if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)
        if isinstance(df_m.columns, pd.MultiIndex): df_m.columns = df_m.columns.get_level_values(0)
        for df in [df_w, df_m]:
            macd = df.ta.macd()
            df['MACD'] = macd['MACD_12_26_9']
            df['Signal'] = macd['MACDs_12_26_9']
            df['K'] = df.ta.stoch(k=14, d=3)['STOCHk_14_3_3']
        return {'W': df_w, 'M': df_m}
    except: return None

def detectar_engano(df):
    k_actual = round(df.iloc[-1]['K'], 1)
    for i in range(1, 5):
        curr = df.iloc[-i]; prev = df.iloc[-i-1]
        mid_prev = (prev['High'] + prev['Low']) / 2
        if curr['Low'] < prev['Low'] and curr['Close'] > mid_prev:
            return "ALCISTA 🟢", ("Esta Sem" if i==1 else f"Hace {i-1} Sem"), k_actual
        if curr['High'] > prev['High'] and curr['Close'] < mid_prev:
            return "BAJISTA 🔴", ("Esta Sem" if i==1 else f"Hace {i-1} Sem"), k_actual
    return "SIN VELA", "---", k_actual

with st.sidebar:
    st.header("⚙️ Control")
    selec = st.selectbox("Mercado", list(MERCADOS.keys()))
    lanzar = st.button("🚀 INICIAR BARRIDO")

if lanzar:
    lista = MERCADOS[selec]
    st.info(f"Escaneando {len(lista)} activos...")
    res = []
    bar = st.progress(0)
    for idx, t in enumerate(lista):
        p = analizar_gema(t)
        if p:
            m = p['M'].iloc[-1]; m_p = p['M'].iloc[-2]
            w = p['W'].iloc[-1]; w_p = p['W'].iloc[-2]
            m_i = f"{'S0' if m['MACD']>0 else 'B0'}/{'UP' if m['MACD']>m_p['MACD'] else 'DN'}"
            w_i = "ALCISTA" if w['MACD'] > w_p['MACD'] else "BAJISTA"
            s, a, k = detectar_engano(p['W'])
            pre = "💎" if (s == "ALCISTA 🟢" and m['MACD'] > 0 and k < 25) else ""
            res.append({"Ticker": t, "Premium": pre, "Gatillo": s, "Antig": a, "MACD M": m_i, "MACD S": w_i, "Stoch": k})
        bar.progress((idx+1)/len(lista))
    st.dataframe(pd.DataFrame(res), use_container_width=True)
