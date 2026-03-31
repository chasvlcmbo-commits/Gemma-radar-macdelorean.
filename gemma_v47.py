
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Macdelorean Radar v24",
    page_icon="🦅",
    layout="wide"
)

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

    .stApp { background-color: #080c10; color: #c9d1d9; }
    h1, h2, h3 { color: #00e676 !important; font-family: 'Orbitron', monospace !important; letter-spacing: 2px; }

    div.stButton > button {
        width: 100%; border: 2px solid #00e676;
        background: linear-gradient(135deg, #0a1628 0%, #0d2137 100%);
        color: #00e676; font-weight: bold; font-size: 18px; padding: 14px;
        font-family: 'Orbitron', monospace; letter-spacing: 3px;
        transition: all 0.3s; text-transform: uppercase;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #00e676 0%, #00bcd4 100%);
        color: #000000; box-shadow: 0 0 20px #00e676aa;
    }
    .stCheckbox label { color: #00e676 !important; font-family: 'Share Tech Mono', monospace; font-size: 13px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #0d1117; border-bottom: 1px solid #00e676; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-family: 'Orbitron', monospace; font-size: 11px; }
    .stTabs [aria-selected="true"] { color: #00e676 !important; border-bottom: 2px solid #00e676; }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #00e676, #00bcd4); }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; color: #ffffff; font-family: 'Share Tech Mono', monospace; }
    div[data-testid="stMetricLabel"] { color: #8b949e; font-family: 'Share Tech Mono', monospace; }
    .stDataFrame { border: 1px solid #1e3a2f; }
    section[data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #1e3a2f; }
    hr { border-color: #1e3a2f; }
    .streamlit-expanderHeader { color: #00e676 !important; font-family: 'Share Tech Mono', monospace; }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 1. UNIVERSO MASIVO DE ACTIVOS — ~1400 TICKERS
# ==============================================================================

UNIVERSO = {

    # ──────────────────────────────────────────────
    "🇺🇸 DOW JONES 30": [
        "MMM","AXP","AMGN","AAPL","BA","CAT","CVX","CSCO","KO","DIS",
        "DOW","GS","HD","HON","IBM","INTC","JNJ","JPM","MCD","MRK",
        "MSFT","NKE","PG","CRM","TRV","UNH","VZ","V","WMT","AMZN"
    ],

    # ──────────────────────────────────────────────
    "🚀 NASDAQ 100 COMPLETO": [
        "AAPL","MSFT","NVDA","AMZN","META","TSLA","GOOGL","GOOG","AVGO","COST",
        "NFLX","TMUS","AMD","CSCO","ADBE","PEP","AZN","QCOM","TXN","ISRG",
        "INTU","AMAT","HON","CMCSA","BKNG","VRTX","REGN","MU","PANW","ADI",
        "LRCX","KLAC","SNPS","CDNS","MELI","ASML","MDLZ","GILD","CTAS","ADP",
        "FTNT","MAR","ABNB","MCHP","ORLY","KDP","DXCM","WDAY","PAYX","MNST",
        "ROST","BIIB","IDXX","PCAR","EA","FAST","CTSH","ODFL","VRSK","CEG",
        "DDOG","ZS","CRWD","TEAM","NXPI","EXC","AEP","XEL","ILMN","ON",
        "GEHC","TTWO","SBUX","PDD","ALGN","ENPH","WBD","FANG","DLTR","SIRI",
        "ZM","EBAY","PYPL","LCID","RIVN","HOOD","COIN","MARA","RIOT","LULU",
        "CHTR","BKR","CSX","FISV","ANSS","CPRT","CSGP","DKNG","GFS","HTHT"
    ],

    # ──────────────────────────────────────────────
    "📈 S&P 500 — FINANCIALS & INDUSTRIALS": [
        "JPM","BAC","WFC","GS","MS","C","BK","USB","PNC","TFC",
        "COF","AXP","DFS","SYF","ALLY","FITB","KEY","RF","HBAN","CFG",
        "MTB","ZION","CMA","PBCT","FHN","SIVB","SBNY","WAL","EWBC","PACW",
        "BLK","SCHW","TROW","IVZ","BEN","AMG","APAM","VRTS","SEIC","FDS",
        "ICE","CME","CBOE","NDAQ","MKTX","VIRT","LPLA","RJF","SF","PIPR",
        "MMC","AON","AJG","WTW","HIG","MET","PRU","AFL","ALL","TRV",
        "CB","AIG","PGR","CINF","GL","LNC","UNM","PFG","AIZ","EG",
        "GE","HON","MMM","CAT","DE","EMR","ETN","PH","ROK","AME",
        "ITW","DOV","GGG","GNRC","XYL","REXNORD","FLS","IDEX","IR","TT",
        "CARR","OTIS","RTX","LMT","NOC","GD","LHX","BAH","LDOS","SAIC"
    ],

    # ──────────────────────────────────────────────
    "📈 S&P 500 — HEALTHCARE & CONSUMER": [
        "UNH","CVS","CI","HUM","CNC","MOH","ELV","WCG","OSH","ALHC",
        "JNJ","PFE","ABT","MRK","LLY","BMY","GILD","AMGN","REGN","VRTX",
        "BIIB","ALNY","MRNA","BNTX","SGEN","EXAS","ILMN","PACB","TDOC","ONEM",
        "TMO","DHR","A","WAT","MTD","PKI","IQV","CTLT","CRL","MEDP",
        "MDT","SYK","BSX","EW","DXCM","RMD","HOLX","ZBH","BDX","COO",
        "AMZN","WMT","COST","TGT","HD","LOW","TJX","ROST","BURL","FIVE",
        "MCD","SBUX","YUM","QSR","DPZ","CMG","WING","SHAK","JACK","DENN",
        "NKE","LULU","VFC","PVH","HBI","UA","SKX","CROX","DECK","WWW",
        "PG","KO","PEP","MDLZ","GIS","CPB","CAG","SJM","HRL","MKC",
        "PM","MO","BTI","MNST","KDP","CELH","FIZZ","SAM","BF-B","TAP"
    ],

    # ──────────────────────────────────────────────
    "📈 S&P 500 — ENERGY & UTILITIES": [
        "XOM","CVX","COP","EOG","PXD","DVN","MRO","APA","HES","FANG",
        "SLB","HAL","BKR","OIS","OIH","NOV","DRQ","HP","NE","PTEN",
        "VLO","MPC","PSX","DK","PBF","HFC","CLMT","PARR","CALUMET","ALJ",
        "KMI","WMB","ET","EPD","MPLX","PAA","TRGP","OKE","LNG","FLEX",
        "DUK","SO","NEE","AEP","EXC","XEL","D","SRE","PEG","ED",
        "WEC","ES","ETR","CNP","CMS","LNT","PNW","OGE","NI","EVRG",
        "NRG","VST","CEG","AES","BEP","CWEN","AMPS","NOVA","RUN","SEDG",
        "ENPH","FSLR","SPWR","CSIQ","JKS","DAQO","RUN","ARRY","NOVA","SHLS"
    ],

    # ──────────────────────────────────────────────
    "📈 S&P 500 — TECH & REITS": [
        "AAPL","MSFT","NVDA","GOOGL","META","TSLA","AVGO","ORCL","IBM","QCOM",
        "TXN","ADI","MCHP","LRCX","AMAT","KLAC","SNPS","CDNS","ANSS","EPAM",
        "PAYC","PCTY","HUBS","DOMO","COUP","VEEV","OKTA","ZI","BOX","DBX",
        "TWLO","BAND","EGHT","MSGM","CCCS","ALKT","JAMF","DOCU","SMAR","MNDY",
        "AMT","CCI","SBAC","UNIT","LAMR","OUT","DLR","EQIX","QTS","CONE",
        "O","WPC","NNN","STOR","VICI","GLPI","MGP","EPR","SPG","MAC",
        "EQR","AVB","ESS","UDR","AIV","MAA","CPT","INVH","AMH","SUI",
        "ELS","PSA","EXR","CUBE","LSI","NSA","COLD","STAG","ADC","TRNO"
    ],

    # ──────────────────────────────────────────────
    "🇩🇪 DAX 40 COMPLETO": [
        "SAP.DE","SIE.DE","AIR.DE","ALV.DE","DTE.DE","MBG.DE","VOW3.DE",
        "BMW.DE","BAS.DE","ADS.DE","IFX.DE","DHL.DE","MUV2.DE","DB1.DE",
        "BEI.DE","RWE.DE","EOAN.DE","SY1.DE","BAYN.DE","DTG.DE","HEN3.DE",
        "VNA.DE","CON.DE","PAH3.DE","MTX.DE","HEI.DE","MRK.DE","BNR.DE",
        "HNR1.DE","ZAL.DE","FRE.DE","FME.DE","QIA.DE","PUM.DE","SHL.DE",
        "ENR.DE","EVT.DE","1COV.DE","SON22.DE","SXS.DE"
    ],

    # ──────────────────────────────────────────────
    "🇩🇪 MDAX ALEMANIA (Mid Caps)": [
        "AIXA.DE","AFX.DE","BNR.DE","BOSS.DE","COP.DE","EVK.DE","FPE3.DE",
        "G1A.DE","GXI.DE","HAG.DE","HHFA.DE","HOT.DE","IFX.DE","JEN.DE",
        "K+S.DE","KGX.DE","KSB3.DE","LEG.DE","LHA.DE","MBB.DE","MDG1.DE",
        "MRCG.DE","NDX1.DE","NEM.DE","O2D.DE","PSM.DE","RAA.DE","RSL2.DE",
        "S92.DE","SDF.DE","SDAX.DE","SGL.DE","SMHN.DE","ST5.DE","STO3.DE",
        "SY1.DE","TKA.DE","TUI1.DE","VBK.DE","WAF.DE","WCH.DE","WIN.DE"
    ],

    # ──────────────────────────────────────────────
    "🇪🇸 IBEX 35 COMPLETO": [
        "ITX.MC","IBE.MC","BBVA.MC","SAN.MC","CABK.MC","TEF.MC","ACS.MC",
        "FER.MC","AENA.MC","AMS.MC","REP.MC","CLNX.MC","IAG.MC","ENG.MC",
        "ANA.MC","GRF.MC","RED.MC","MTS.MC","ACX.MC","BKT.MC","MAP.MC",
        "TL5.MC","MEL.MC","PHM.MC","SAB.MC","IDR.MC","COL.MC","LOG.MC",
        "FDR.MC","ROVI.MC","SOL.MC","UNI.MC","VIS.MC","ELE.MC","CIE.MC"
    ],

    # ──────────────────────────────────────────────
    "🇪🇸 BME GROWTH (Small Caps España)": [
        "OHLA.MC","MDF.MC","CASH.MC","ERIZ.MC","CLNX.MC","ENAV.MC",
        "ALNT.MC","BAIN.MC","DGRN.MC","ECR.MC","ELEX.MC","FLUI.MC",
        "HERN.MC","HGT.MC","LABE.MC","LFDS.MC","MDLN.MC","MEHR.MC",
        "MENT.MC","MXOC.MC","MYMD.MC","NMAS.MC","NRGY.MC","NTGY.MC",
        "OHLA.MC","ORYC.MC","PBIT.MC","PCAS.MC","PRTC.MC","RLIA.MC"
    ],

    # ──────────────────────────────────────────────
    "🇫🇷 CAC 40 COMPLETO": [
        "MC.PA","OR.PA","RMS.PA","TTE.PA","SAN.PA","AIR.PA","SU.PA",
        "BNP.PA","SAF.PA","EL.PA","AXA.PA","DG.PA","KER.PA","DSY.PA",
        "STLAP.PA","RI.PA","CAP.PA","GLE.PA","ORA.PA","BN.PA","EN.PA",
        "LR.PA","ACA.PA","CA.PA","ML.PA","VIE.PA","SGO.PA","HO.PA",
        "ATO.PA","PUB.PA","WLN.PA","URW.PA","RNO.PA","VIV.PA","ENGI.PA",
        "STM.PA","TEP.PA","BOL.PA","ERF.PA","AF.PA"
    ],

    # ──────────────────────────────────────────────
    "🇫🇷 SBF 120 FRANCIA (Mid Caps)": [
        "ABCA.PA","ALSTOM.PA","AMUN.PA","APAM.PA","ATOS.PA","BIC.PA",
        "BIGBEN.PA","BIM.PA","BNB.PA","CHSR.PA","CNP.PA","COFA.PA",
        "DBG.PA","DEC.PA","FNAC.PA","GAM.PA","GTT.PA","HLO.PA",
        "IDP.PA","ILD.PA","IMVD.PA","INEA.PA","IPSO.PA","JCDECAUX.PA",
        "KOF.PA","LACR.PA","LDL.PA","LI.PA","LOUP.PA","MANU.PA",
        "MCPHY.PA","MEDCL.PA","MF.PA","MGDYN.PA","NEXANS.PA","NXI.PA",
        "OPM.PA","OREGE.PA","PKGD.PA","PLXS.PA","RBAL.PA","REMY.PA",
        "SAFT.PA","SBMO.PA","SCOR.PA","SEB.PA","SESG.PA","SPIE.PA","TITAN.PA"
    ],

    # ──────────────────────────────────────────────
    "🇬🇧 FTSE 100 COMPLETO": [
        "SHEL.L","AZN.L","HSBA.L","ULVR.L","BP.L","GSK.L","RIO.L",
        "DGE.L","BHP.L","REL.L","NG.L","BATS.L","VOD.L","LLOY.L",
        "NWG.L","BARC.L","PRU.L","LGEN.L","AV.L","STAN.L","ABF.L",
        "ANTO.L","AUTO.L","BA.L","BNZL.L","BT-A.L","CCH.L","CPG.L",
        "CNA.L","CRDA.L","DCC.L","DPH.L","EZJ.L","FERG.L","FLTR.L",
        "GLEN.L","HLMA.L","HL.L","IHG.L","IMB.L","ITV.L","JD.L",
        "KGF.L","LAND.L","MNG.L","MRO.L","NXT.L","OCDO.L","PSN.L",
        "PSON.L","RKT.L","RR.L","RS1.L","SGE.L","SMDS.L","SMIN.L",
        "SKG.L","SPX.L","SSE.L","SBRY.L","SVT.L","TSCO.L","WPP.L",
        "WTB.L","UU.L","TUI.L","AAL.L","ADM.L","AGK.L","ANTO.L",
        "AHT.L","BME.L","BOO.L","BRBY.L","BVS.L","CCC.L","CLDN.L",
        "CNE.L","COB.L","CYBG.L","DARK.L","DLN.L","ECM.L","ENT.L",
        "EXPN.L","FCIT.L","FRES.L","GRG.L","HIK.L","HWDN.L","ICG.L",
        "III.L","IMI.L","INF.L","ITRK.L","JET.L","JET2.L","JMAT.L",
        "JUST.L","LSEG.L","LMP.L","MNDI.L","MONY.L","MTRO.L","MUT.L"
    ],

    # ──────────────────────────────────────────────
    "🌍 EUROSTOXX 50": [
        "ASML.AS","ADYEN.AS","INGA.AS","PHIA.AS","HEIA.AS","NN.AS","RAND.AS","WKL.AS","ABN.AS","UMG.AS",
        "SAP.DE","SIE.DE","ALV.DE","MBG.DE","BMW.DE","BAYN.DE","ADS.DE","BAS.DE","MUV2.DE","DTE.DE",
        "MC.PA","OR.PA","TTE.PA","SAN.PA","BNP.PA","AIR.PA","SU.PA","AXA.PA","EL.PA","DG.PA",
        "ITX.MC","BBVA.MC","SAN.MC","IBE.MC","REP.MC",
        "ENI.MI","ISP.MI","UCG.MI","ENEL.MI","TIT.MI",
        "NESN.SW","ROG.SW","NOVN.SW",
        "NOKIA.HE","NESTE.HE"
    ],

    # ──────────────────────────────────────────────
    "🇮🇹 FTSE MIB ITALIA": [
        "ENI.MI","ISP.MI","UCG.MI","ENEL.MI","TIT.MI","G.MI","MB.MI",
        "RACE.MI","LDO.MI","STM.MI","PRY.MI","BAMI.MI","MONC.MI","SRG.MI",
        "PST.MI","ORN.MI","ERG.MI","BMPS.MI","CPR.MI","FCA.MI","STLAM.MI",
        "CNH.MI","A2A.MI","AMP.MI","AZM.MI","BMED.MI","BC.MI","BZU.MI",
        "CRDI.MI","DIA.MI","DIG.MI","EXO.MI","FILA.MI","FNM.MI","GEO.MI",
        "IVG.MI","MFB.MI","MFEA.MI","MG.MI"
    ],

    # ──────────────────────────────────────────────
    "🇯🇵 NIKKEI 225 (ADRs disponibles en USA)": [
        "TM","HMC","SONY","NTT","NTDOY","FUJIY","KYOCY","MUFG","SMFG","MFG",
        "IX","KB","SHI","FANUY","HTHIY","ISUZY","KDDIY","KYCCF","MARUY","MSBHY",
        "NIDEC","NIPNF","NPSNY","NSANY","OTSKY","PCRFY","RICOY","SEKEY","SFUN","SGIOY",
        "SHCAY","SHNNY","SIEGY","SKLTY","SSDOY","SSUNY","STITF","STSFY","SVNDY","TCEHY",
        "TKHVY","TKOMY","TMSNY","TNABY","TOELY","TRHCY","TRYIY","TTDKY","TWTDY","TYEKF"
    ],

    # ──────────────────────────────────────────────
    "⚡ ETFs USA — SECTORES": [
        "XLK","XLF","XLV","XLE","XLC","XLY","XLP","XLI","XLB","XLRE","XLU",
        "VGT","VFH","VHT","VDE","VOX","VCR","VDC","VIS","VAW","VNQ","IDU",
        "FNCL","FHLC","FENY","FCOM","FDIS","FSTA","FIDU","FMAT","FREL","FUTY"
    ],

    # ──────────────────────────────────────────────
    "⚡ ETFs USA — ÍNDICES AMPLIOS": [
        "SPY","QQQ","DIA","IWM","VTI","VOO","IVV","RSP","MDY","IJR",
        "VTV","VUG","MTUM","QUAL","VLUE","SIZE","USMV","SPHQ","SPLV","SPHB",
        "ARKK","ARKQ","ARKW","ARKG","ARKF","ARKX","PRNT","IZRL","ARKB","CTRU"
    ],

    # ──────────────────────────────────────────────
    "⚡ ETFs INTERNACIONALES": [
        "EWZ","EEM","EFA","VEA","IEFA","VWO","IEMG","FXI","MCHI","KWEB",
        "EWJ","EWY","EWT","EWA","EWC","EWG","EWQ","EWI","EWP","EWU",
        "EWH","EWS","EWM","EWN","EWD","EWL","EWO","EWK","EZU","HEDJ",
        "DBJP","DBEF","DBEU","HEFA","DXJ","HEWJ","HEZU","HSCZ","FLKR","FLJP"
    ],

    # ──────────────────────────────────────────────
    "⚡ ETFs TEMÁTICOS & APALANCADOS": [
        "SMH","SOXX","XBI","TAN","ICLN","PBW","LIT","URA","REMX","COPX",
        "BOTZ","ROBO","IRBO","AIQ","WCLD","CLOU","BUG","HACK","CIBR","IHAK",
        "SQQQ","TQQQ","SPXU","UPRO","SPXS","SDOW","UDOW","LABD","LABU","UVXY",
        "VXX","SVXY","VIXY","UVIX","SVOL","ZIVB","VIXM","VXZ","VIIX","TVIX",
        "GLD","SLV","IAU","SGOL","PHYS","PSLV","PPLT","PALL","GDX","GDXJ",
        "SIL","SILJ","NUGT","DUST","JNUG","JDST","RING","GOAU","SGDM","SGDJ",
        "USO","UNG","BNO","DBO","BOIL","KOLD","UGA","CORN","WEAT","SOYB",
        "TLT","IEF","SHY","HYG","LQD","JNK","BNDX","EMB","PCY","BWX",
        "MSTR","COIN","MARA","RIOT","CLSK","HUT","BTBT","CIFR","CORZ","WULF"
    ],

    # ──────────────────────────────────────────────
    "🎯 GROWTH & DISRUPTIVAS USA": [
        "NVDA","AMD","PLTR","CRWD","DDOG","ZS","NET","SNOW","OKTA","TWLO",
        "BILL","GTLB","HUBS","CFLT","MDB","ESTC","DOMO","APPN","ALTR","PEGA",
        "NOW","WDAY","VEEV","COUP","PCTY","PAYC","RNG","SMAR","MNDY","JAMF",
        "DOCU","BOX","DBX","DRCT","FIVN","NICE","FOUR","BRZE","AMPL","ASAN",
        "IONQ","RGTI","QUBT","QBTS","IBM","MSFT","GOOGL","ORCL","ADBE","CRM",
        "UBER","LYFT","ABNB","DASH","GRUB","CART","TOST","PAR","SHAK","NURO",
        "TSLA","LCID","RIVN","FSR","GOEV","WKHS","SOLO","AYRO","NKLA","HYLN",
        "JOBY","ACHR","LILM","EVTOL","AAL","UAL","DAL","LUV","ALK","SAVE"
    ],

    # ──────────────────────────────────────────────
    "🎯 SMALL CAPS & ESPECULATIVOS USA": [
        "SOFI","AFRM","HOOD","DKNG","GME","AMC","TLRY","SNDL","ACB","HEXO",
        "CRON","OGI","VEXT","TPVG","IIPR","MSOS","YOLO","MJ","THCX","CNBS",
        "UPST","AI","SAVA","OPEN","SPCE","QS","NKLA","RIDE","XL","ATLIS",
        "CVNA","CROX","ELF","CELH","HIMS","ACMR","LAZR","LIDR","INVZ","OUST",
        "MVIS","VUZI","KOPN","KTOS","AVAV","RKLB","MNTS","ASTS","LUNR","RDW",
        "OXY","HAL","SLB","APA","DVN","MRO","HES","COP","EOG","FANG",
        "VLO","MPC","PSX","DK","PBF","KMI","WMB","ET","EPD","MPLX",
        "AGNC","NLY","STWD","BXMT","ABR","RC","GPMT","KREF","LADR","TRTX",
        "O","WPC","NNN","VICI","GLPI","STOR","ADC","EPR","SRC","PINE"
    ],

    # ──────────────────────────────────────────────
    "💎 MEGA CAPS GLOBALES": [
        "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","LLY","V",
        "UNH","JPM","XOM","MA","JNJ","WMT","PG","HD","MRK","CVX",
        "ABBV","KO","BAC","PEP","COST","TMO","CRM","ACN","MCD","CSCO",
        "ABT","ORCL","ADBE","NKE","TXN","DHR","NEE","LIN","PM","RTX",
        "NESN.SW","ROG.SW","NOVN.SW","SHEL.L","AZN.L","HSBA.L","BP.L","GSK.L",
        "MC.PA","OR.PA","ASML.AS","SAP.DE","SIE.DE","ALV.DE","TM","SONY","MUFG"
    ],
}


# ==============================================================================
# 2. INTELIGENCIA TÉCNICA (sin cambios respecto a v23)
# ==============================================================================

def procesar_datos(ticker, incluir_4h=False):
    try:
        df_d = yf.download(ticker, period="1y",  interval="1d",  progress=False, auto_adjust=True)
        df_w = yf.download(ticker, period="3y",  interval="1wk", progress=False, auto_adjust=True)
        df_m = yf.download(ticker, period="5y",  interval="1mo", progress=False, auto_adjust=True)

        if df_d.empty or df_w.empty or df_m.empty:
            return None

        if isinstance(df_d.columns, pd.MultiIndex): df_d = df_d.xs(ticker, axis=1, level=1)
        if isinstance(df_w.columns, pd.MultiIndex): df_w = df_w.xs(ticker, axis=1, level=1)
        if isinstance(df_m.columns, pd.MultiIndex): df_m = df_m.xs(ticker, axis=1, level=1)

        dfs = [df_d, df_w, df_m]

        # 4h solo si se necesita (evita peticiones extra innecesarias)
        df_4h = pd.DataFrame()
        if incluir_4h:
            try:
                df_4h = yf.download(ticker, period="60d", interval="1h", progress=False, auto_adjust=True)
                if isinstance(df_4h.columns, pd.MultiIndex): df_4h = df_4h.xs(ticker, axis=1, level=1)
                # Resamplear 1h a 4h
                df_4h = df_4h.resample('4h').agg({
                    'Open': 'first', 'High': 'max', 'Low': 'min',
                    'Close': 'last', 'Volume': 'sum'
                }).dropna()
                dfs.append(df_4h)
            except:
                df_4h = pd.DataFrame()

        for df in dfs:
            if df.empty: continue
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            if macd is not None:
                df['MACD']   = macd['MACD_12_26_9']
                df['Signal'] = macd['MACDs_12_26_9']
            if len(df) > 15:
                stoch = df.ta.stoch(k=14, d=3)
                if stoch is not None:
                    df['K'] = stoch['STOCHk_14_3_3']

        return {'D': df_d, 'W': df_w, 'M': df_m, '4H': df_4h}
    except:
        return None


def check_punto_b(df, timeframe="D"):
    """
    Detecta módulo de arranque (Punto B) en acción del precio.

    Busca la estructura A -> B -> C donde:
    - A = primer mínimo
    - B = máximo entre A y C (nivel de ruptura)
    - C = segundo mínimo
    - El precio actual ha roto o está cerca de romper B

    Tiempos válidos de formación (A a C):
    - 4H:  35 a 90 velas
    - D:   40 a 60 velas
    - W:   13 a 30 velas
    - M:   7  a 12 velas

    Buena oscilación: C < A
    Mala oscilación:  C > A

    Devuelve: (encontrado, tipo, nivel_b, tp1, tp2, info_dict)
    """
    min_velas = {"4H": 35, "D": 40, "W": 13, "M": 7}.get(timeframe, 40)
    max_velas = {"4H": 90, "D": 60, "W": 30, "M": 12}.get(timeframe, 60)

    if df is None or df.empty or len(df) < min_velas + 10:
        return False, "", 0, 0, 0, {}

    close  = df['Close']
    high   = df['High']
    low    = df['Low']
    n      = len(df)

    # Buscar estructura A-B-C en ventana reciente
    # Ventana de búsqueda: últimas max_velas*2 velas
    ventana = min(n - 5, int(max_velas * 1.5))
    df_win  = df.iloc[-ventana:]
    c_win   = df_win['Close']
    l_win   = df_win['Low']
    h_win   = df_win['High']
    nw      = len(df_win)

    mejor = None

    # Buscar todos los mínimos locales como candidatos a A
    for ia in range(3, nw - min_velas - 3):
        # A debe ser mínimo local
        if not (l_win.iloc[ia] < l_win.iloc[ia-1] and
                l_win.iloc[ia] < l_win.iloc[ia-2] and
                l_win.iloc[ia] < l_win.iloc[ia+1] and
                l_win.iloc[ia] < l_win.iloc[ia+2]):
            continue

        precio_a = l_win.iloc[ia]

        # Buscar B: máximo local DESPUÉS de A
        for ib in range(ia + 3, nw - min_velas//2 - 3):
            if not (h_win.iloc[ib] > h_win.iloc[ib-1] and
                    h_win.iloc[ib] > h_win.iloc[ib-2] and
                    h_win.iloc[ib] > h_win.iloc[ib+1] and
                    h_win.iloc[ib] > h_win.iloc[ib+2]):
                continue

            nivel_b = h_win.iloc[ib]

            # B debe estar por encima de A
            if nivel_b <= precio_a:
                continue

            # Buscar C: mínimo local DESPUÉS de B
            for ic in range(ib + 3, nw - 2):
                if not (l_win.iloc[ic] < l_win.iloc[ic-1] and
                        l_win.iloc[ic] < l_win.iloc[ic-2] and
                        l_win.iloc[ic] < l_win.iloc[ic+1] and
                        l_win.iloc[ic] < l_win.iloc[ic+2]):
                    continue

                precio_c = l_win.iloc[ic]

                # C debe estar por debajo de B
                if precio_c >= nivel_b:
                    continue

                # Verificar tiempo de formación A->C
                duracion_ac = ic - ia
                if not (min_velas <= duracion_ac <= max_velas):
                    continue

                # Verificar que precio actual está cerca o por encima de B
                precio_actual = close.iloc[-1]

                # Solo nos interesan estructuras recientes: C en últimas max_velas/2 velas
                velas_desde_c = nw - 1 - ic
                max_desde_c = {"4H": 15, "D": 10, "W": 6, "M": 3}.get(timeframe, 10)
                if velas_desde_c > max_desde_c:
                    continue


                # Clasificar oscilación
                if precio_c < precio_a:
                    tipo_osc = "🟢 BUENA OSCILACIÓN"
                    min_abs  = precio_c
                else:
                    tipo_osc = "🟡 MALA OSCILACIÓN"
                    min_abs  = precio_a

                # Calcular altura del módulo y targets
                altura   = nivel_b - min_abs
                # ── FILTRO ALTURA MÍNIMA DEL MÓDULO ──
                pct_min = {"4H": 0.06, "D": 0.08, "W": 0.10, "M": 0.15}.get(timeframe, 0.08)
                if altura < nivel_b * pct_min:
                    continue
                tp1      = round(min_abs + altura * 1.618, 2)
                tp2      = round(min_abs + altura * 2.0,   2)

                # Precio rompiendo B o muy cerca (dentro del 2%)
                roto_b    = precio_actual >= nivel_b
                cerca_b   = precio_actual >= nivel_b * 0.98

                if not cerca_b:
                    continue

                # ── FILTRO MADUREZ ALCISTA ──
                if roto_b:
                    # Contar velas desde que rompió B (desde C hacia adelante)
                    velas_tras_ruptura = 0
                    for k_idx in range(ic + 1, nw):
                        if c_win.iloc[k_idx] >= nivel_b:
                            velas_tras_ruptura = nw - k_idx
                            break
                    # Descartar si lleva más de 5 velas desde la ruptura
                    if velas_tras_ruptura > 5:
                        continue
                    # Descartar si precio ya superó TP1
                    if precio_actual >= tp1:
                        continue
                    # Descartar si precio retrocedió más del 50% de la altura por debajo de B
                    precio_minimo_tras_b = min(c_win.iloc[ic+1:].values) if ic+1 < nw else precio_actual
                    nivel_invalidacion = nivel_b - (altura * 0.5)
                    if precio_minimo_tras_b < nivel_invalidacion:
                        continue

                estado = "✅ ROTO" if roto_b else "⚡ CERCA"
                velas_ruptura = velas_tras_ruptura if roto_b else 0

                mejor = {
                    "tipo":            tipo_osc,
                    "nivel_b":         round(nivel_b, 2),
                    "precio_a":        round(precio_a, 2),
                    "precio_c":        round(precio_c, 2),
                    "tp1":             tp1,
                    "tp2":             tp2,
                    "estado_b":        estado,
                    "duracion_velas":  duracion_ac,
                    "velas_desde_c":   velas_desde_c,
                    "velas_ruptura":   velas_ruptura,
                }
                break  # tomamos el primer C válido para este B
            if mejor:
                break
        if mejor:
            break

    if mejor:
        return True, mejor["tipo"], mejor["nivel_b"], mejor["tp1"], mejor["tp2"], mejor

    # ══════════════════════════════════════════
    # ESTRUCTURA BAJISTA: A(max) -> B(min) -> C(max)
    # ══════════════════════════════════════════
    mejor = None

    for ia in range(3, nw - min_velas - 3):
        # A debe ser máximo local
        if not (h_win.iloc[ia] > h_win.iloc[ia-1] and
                h_win.iloc[ia] > h_win.iloc[ia-2] and
                h_win.iloc[ia] > h_win.iloc[ia+1] and
                h_win.iloc[ia] > h_win.iloc[ia+2]):
            continue

        precio_a = h_win.iloc[ia]

        # Buscar B: mínimo local DESPUÉS de A
        for ib in range(ia + 3, nw - min_velas//2 - 3):
            if not (l_win.iloc[ib] < l_win.iloc[ib-1] and
                    l_win.iloc[ib] < l_win.iloc[ib-2] and
                    l_win.iloc[ib] < l_win.iloc[ib+1] and
                    l_win.iloc[ib] < l_win.iloc[ib+2]):
                continue

            nivel_b = l_win.iloc[ib]

            # B debe estar por debajo de A
            if nivel_b >= precio_a:
                continue

            # Buscar C: máximo local DESPUÉS de B
            for ic in range(ib + 3, nw - 2):
                if not (h_win.iloc[ic] > h_win.iloc[ic-1] and
                        h_win.iloc[ic] > h_win.iloc[ic-2] and
                        h_win.iloc[ic] > h_win.iloc[ic+1] and
                        h_win.iloc[ic] > h_win.iloc[ic+2]):
                    continue

                precio_c = h_win.iloc[ic]

                # C debe estar por encima de B
                if precio_c <= nivel_b:
                    continue

                # Verificar tiempo de formación A->C
                duracion_ac = ic - ia
                if not (min_velas <= duracion_ac <= max_velas):
                    continue

                # Solo estructuras recientes
                velas_desde_c = nw - 1 - ic
                max_desde_c = {"4H": 15, "D": 10, "W": 6, "M": 3}.get(timeframe, 10)
                if velas_desde_c > max_desde_c:
                    continue

                precio_actual = close.iloc[-1]

                # Clasificar oscilación bajista
                if precio_c > precio_a:
                    tipo_osc = "🟢 BUENA OSC. BAJISTA"
                    max_abs  = precio_c
                else:
                    tipo_osc = "🟡 MALA OSC. BAJISTA"
                    max_abs  = precio_a

                # Altura y targets bajistas
                altura = max_abs - nivel_b
                tp1    = round(max_abs - altura * 1.618, 2)
                tp2    = round(max_abs - altura * 2.0,   2)

                # ── FILTRO ALTURA MÍNIMA DEL MÓDULO ──
                pct_min = {"4H": 0.06, "D": 0.08, "W": 0.10, "M": 0.15}.get(timeframe, 0.08)
                if altura < nivel_b * pct_min:
                    continue
                # Precio rompiendo B a la baja o muy cerca
                roto_b  = precio_actual <= nivel_b
                cerca_b = precio_actual <= nivel_b * 1.02

                if not cerca_b:
                    continue

                # ── FILTRO MADUREZ BAJISTA ──
                if roto_b:
                    # Contar velas desde que rompió B
                    velas_tras_ruptura = 0
                    for k_idx in range(ic + 1, nw):
                        if h_win.iloc[k_idx] <= nivel_b:
                            velas_tras_ruptura = nw - k_idx
                            break
                    # Descartar si lleva más de 5 velas desde la ruptura
                    if velas_tras_ruptura > 5:
                        continue
                    # Descartar si precio ya bajó de TP1
                    if precio_actual <= tp1:
                        continue
                    # Descartar si precio rebotó más del 50% de la altura por encima de B
                    precio_maximo_tras_b = max(h_win.iloc[ic+1:].values) if ic+1 < nw else precio_actual
                    nivel_invalidacion = nivel_b + (altura * 0.5)
                    if precio_maximo_tras_b > nivel_invalidacion:
                        continue

                estado = "✅ ROTO" if roto_b else "⚡ CERCA"
                velas_ruptura = velas_tras_ruptura if roto_b else 0

                mejor = {
                    "tipo":           tipo_osc,
                    "nivel_b":        round(nivel_b, 2),
                    "precio_a":       round(precio_a, 2),
                    "precio_c":       round(precio_c, 2),
                    "tp1":            tp1,
                    "tp2":            tp2,
                    "estado_b":       estado,
                    "duracion_velas": duracion_ac,
                    "velas_desde_c":  velas_desde_c,
                    "velas_ruptura":  velas_ruptura,
                }
                break
            if mejor:
                break
        if mejor:
            break

    if mejor:
        return True, mejor["tipo"], mejor["nivel_b"], mejor["tp1"], mejor["tp2"], mejor
    return False, "", 0, 0, 0, {}


def check_vela_engano(df, idx=-1):
    if len(df) < abs(idx) + 2 or 'K' not in df.columns:
        return False, "", 0, 0
    curr = df.iloc[idx]; prev = df.iloc[idx - 1]
    mid_prev = (prev['High'] + prev['Low']) / 2
    k = curr['K']
    if (curr['Low'] < prev['Low']) and (curr['Close'] > mid_prev) and (k < 20.0):
        return True, "ALCISTA 🟢", k, min(curr['Low'], prev['Low'])
    if (curr['High'] > prev['High']) and (curr['Close'] < mid_prev) and (k > 80.0):
        return True, "BAJISTA 🔴", k, max(curr['High'], prev['High'])
    return False, "", k, 0


def encontrar_swings(serie, es_minimo=True, min_dist=3):
    """
    Detecta swing points reales en una serie.
    min_dist: velas mínimas de separación entre swings.
    """
    swings = []
    valores = serie.values
    indices = list(range(len(valores)))
    for i in range(min_dist, len(valores) - min_dist):
        ventana_izq = valores[i - min_dist:i]
        ventana_der = valores[i + 1:i + min_dist + 1]
        if es_minimo:
            if valores[i] < min(ventana_izq) and valores[i] < min(ventana_der):
                swings.append(i)
        else:
            if valores[i] > max(ventana_izq) and valores[i] > max(ventana_der):
                swings.append(i)
    return swings


def check_divergencia(df, timeframe="D"):
    """
    Divergencia real basada en swing points del MACD.
    Devuelve: (encontrada, tipo, duracion_str, antiguedad_str)
    """
    if 'MACD' not in df.columns or 'Close' not in df.columns:
        return False, "", "", ""

    min_velas = {"D": 40, "W": 26, "M": 12}.get(timeframe, 40)
    min_swing_sep = 3

    rango_macd = df['MACD'].max() - df['MACD'].min()
    if rango_macd == 0:
        return False, "", "", ""
    umbral_0 = rango_macd * 0.15

    macd_serie  = df['MACD']
    price_serie = df['Close']
    fecha_serie = df.index

    def formatear_duracion(velas, tf):
        if tf == "D":
            meses = round(velas / 21)
            return f"{meses} meses"
        elif tf == "W":
            meses = round(velas * 7 / 30)
            return f"{meses} meses"
        else:
            return f"{velas} meses"

    def formatear_antiguedad(pos_ultimo, total, tf):
        velas_atras = total - 1 - pos_ultimo
        if tf == "D":
            if velas_atras == 0: return "Hoy"
            if velas_atras < 5:  return f"Hace {velas_atras} días"
            semanas = round(velas_atras / 5)
            return f"Hace {semanas} sem"
        elif tf == "W":
            if velas_atras == 0: return "Esta semana"
            return f"Hace {velas_atras} sem"
        else:
            if velas_atras == 0: return "Este mes"
            return f"Hace {velas_atras} meses"

    total = len(df)

    # ── DIVERGENCIA ALCISTA ──
    mins = encontrar_swings(macd_serie, es_minimo=True, min_dist=min_swing_sep)
    mins_validos = [i for i in mins if macd_serie.iloc[i] < -umbral_0]

    if len(mins_validos) >= 2:
        p1, p2 = mins_validos[-2], mins_validos[-1]
        if (p2 - p1) >= min_velas:
            if price_serie.iloc[p2] < price_serie.iloc[p1] and macd_serie.iloc[p2] > macd_serie.iloc[p1]:
                fuerza    = round(abs(macd_serie.iloc[p2] - macd_serie.iloc[p1]) / rango_macd * 100, 1)
                duracion  = formatear_duracion(p2 - p1, timeframe)
                antiguedad = formatear_antiguedad(p2, total, timeframe)
                return True, f"DIV ALCISTA 📈 ({fuerza}%)", duracion, antiguedad

    # ── DIVERGENCIA BAJISTA ──
    maxs = encontrar_swings(macd_serie, es_minimo=False, min_dist=min_swing_sep)
    maxs_validos = [i for i in maxs if macd_serie.iloc[i] > umbral_0]

    if len(maxs_validos) >= 2:
        p1, p2 = maxs_validos[-2], maxs_validos[-1]
        if (p2 - p1) >= min_velas:
            if price_serie.iloc[p2] > price_serie.iloc[p1] and macd_serie.iloc[p2] < macd_serie.iloc[p1]:
                fuerza    = round(abs(macd_serie.iloc[p1] - macd_serie.iloc[p2]) / rango_macd * 100, 1)
                duracion  = formatear_duracion(p2 - p1, timeframe)
                antiguedad = formatear_antiguedad(p2, total, timeframe)
                return True, f"DIV BAJISTA 📉 ({fuerza}%)", duracion, antiguedad

    return False, "", "", ""


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


def check_cruce_emas(df, velas=4):
    """
    Detecta cruce reciente de EMA50 con EMA200 en las últimas N velas.
    Golden Cross: EMA50 cruza por encima de EMA200 -> alcista
    Death Cross:  EMA50 cruza por debajo de EMA200 -> bajista
    """
    if len(df) < 205:
        return False, ""
    ema50  = df['Close'].ewm(span=50,  adjust=False).mean()
    ema200 = df['Close'].ewm(span=200, adjust=False).mean()

    # Mirar las últimas N+1 velas para detectar cruce
    for i in range(1, velas + 1):
        curr_diff = ema50.iloc[-i]   - ema200.iloc[-i]
        prev_diff = ema50.iloc[-i-1] - ema200.iloc[-i-1]
        if prev_diff < 0 and curr_diff > 0:
            return True, f"✨ GOLDEN CROSS (Hace {i-1} velas)"
        if prev_diff > 0 and curr_diff < 0:
            return True, f"💀 DEATH CROSS (Hace {i-1} velas)"
    return False, ""


def check_macd_estado(df):
    """
    Devuelve el estado del MACD: 'alcista', 'bajista' o 'neutro'
    Alcista: línea MACD por encima de la Signal
    Bajista: línea MACD por debajo de la Signal
    """
    if 'MACD' not in df.columns or 'Signal' not in df.columns or len(df) < 1:
        return 'neutro'
    curr = df.iloc[-1]
    if curr['MACD'] > curr['Signal']:
        return 'alcista'
    if curr['MACD'] < curr['Signal']:
        return 'bajista'
    return 'neutro'


# ==============================================================================
# 3. INTERFAZ
# ==============================================================================

st.markdown("""
<div style='text-align:center; padding: 10px 0 5px 0;'>
    <span style='font-family: Orbitron, monospace; font-size: 2.2rem; font-weight: 900;
                 color: #00e676; letter-spacing: 6px; text-shadow: 0 0 20px #00e676aa;'>
        🦅 MACDELOREAN v24
    </span><br>
    <span style='font-family: Share Tech Mono, monospace; font-size: 0.85rem;
                 color: #8b949e; letter-spacing: 4px;'>
        SISTEMA DE INTELIGENCIA ESTRUCTURAL · UNIVERSO MÁXIMO
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("## 🎛️ PANEL DE CONTROL")
    st.markdown("---")

    st.markdown("### 📊 ÍNDICES A ESCANEAR")

    # Agrupar por región — DEBE ir ANTES de los botones
    grupos = {
        "USA": [k for k in UNIVERSO if any(x in k for x in ["DOW","NASDAQ","S&P","GROWTH","SMALL","MEGA"])],
        "EUROPA": [k for k in UNIVERSO if any(x in k for x in ["DAX","MDAX","IBEX","BME","CAC","SBF","FTSE","EUROS","ITALIA"])],
        "ASIA": [k for k in UNIVERSO if "NIKKEI" in k],
        "ETFs": [k for k in UNIVERSO if "ETF" in k or "TEMAT" in k],
    }
    n_total = sum(len(keys) for keys in grupos.values())

    # Botones rápidos de selección
    col_sel1, col_sel2 = st.columns(2)
    seleccionar_todos   = col_sel1.button("✅ Todos")
    deseleccionar_todos = col_sel2.button("❌ Ninguno")

    if seleccionar_todos:
        for i in range(n_total):
            st.session_state[f"idx_{i}"] = True
    if deseleccionar_todos:
        for i in range(n_total):
            st.session_state[f"idx_{i}"] = False

    st.markdown("")

    indices_seleccionados = []
    key_counter = 0
    for grupo, keys in grupos.items():
        if not keys:
            continue
        st.markdown(f"**{grupo}**")
        for nombre_indice in keys:
            n = len(UNIVERSO[nombre_indice])
            safe_key = f"idx_{key_counter}"
            default_val = st.session_state.get(safe_key, True)
            checked = st.checkbox(f"{nombre_indice} ({n})", value=default_val, key=safe_key)
            if checked:
                indices_seleccionados.append(nombre_indice)
            key_counter += 1
        st.markdown("")

    st.markdown("---")

    st.markdown("### 🔍 FILTROS DE BÚSQUEDA")
    filtro_premium   = st.checkbox("💎 Operaciones Premium (M+W+D)", value=True,  key="f1")
    filtro_velas     = st.checkbox("🕯️ Velas de Engaño (W/M)",       value=True,  key="f2")
    filtro_diverg    = st.checkbox("📐 Divergencias MACD",            value=False, key="f3")
    filtro_macd_combo  = st.checkbox("📡 Radar MACD por Timeframe",    value=False, key="f4")
    filtro_confluencia = st.checkbox("💥 Confluencia Div + Vela",       value=True,  key="f5")
    filtro_emas        = st.checkbox("📈 Cruce EMA 50/200",              value=False, key="f6")
    filtro_puntob      = st.checkbox("🔵 Módulo de Arranque (Punto B)",  value=False, key="f7")

    if filtro_puntob:
        st.markdown("**Timeframes Punto B:**")
        pb_4h = st.checkbox("4H", value=False, key="pb4h")
        pb_d  = st.checkbox("Diario",  value=True,  key="pbd")
        pb_w  = st.checkbox("Semanal", value=True,  key="pbw")
        pb_m  = st.checkbox("Mensual", value=False, key="pbm")
    else:
        pb_4h = pb_d = pb_w = pb_m = False

    if filtro_macd_combo:
        st.markdown("**Estado MACD — selecciona cada TF:**")
        opciones_macd = ["⚪ Cualquiera", "🟢 Alcista", "🔴 Bajista"]
        macd_m = st.selectbox("Mensual (M)", opciones_macd, index=0, key="macd_m")
        macd_w = st.selectbox("Semanal (W)", opciones_macd, index=0, key="macd_w")
        macd_d = st.selectbox("Diario  (D)", opciones_macd, index=0, key="macd_d")
    else:
        macd_m = macd_w = macd_d = "⚪ Cualquiera"

    st.markdown("---")

    st.markdown("### 🧭 DIRECCIÓN")
    dir_alcista = st.checkbox("🟢 Alcistas", value=True, key="dir1")
    dir_bajista = st.checkbox("🔴 Bajistas", value=True, key="dir2")

    st.markdown("---")

    total_tickers = sum(len(UNIVERSO[i]) for i in indices_seleccionados)
    # Estimar tiempo
    seg_est = total_tickers * 0.35
    min_est = int(seg_est // 60)
    seg_r   = int(seg_est % 60)

    st.markdown(f"""
    <div style='background:#0d2137; border:1px solid #00e676; border-radius:6px; padding:12px; text-align:center;'>
        <span style='font-family:Share Tech Mono; color:#8b949e; font-size:11px;'>OBJETIVOS</span><br>
        <span style='font-family:Orbitron; color:#00e676; font-size:2rem; font-weight:700;'>{total_tickers}</span><br>
        <span style='font-family:Share Tech Mono; color:#8b949e; font-size:11px;'>⏱ EST. {min_est}m {seg_r}s</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    lanzar = st.button("🔥 LANZAR RADAR")


# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if lanzar:
    if not indices_seleccionados:
        st.error("⚠️ Selecciona al menos un índice.")
        st.stop()
    if not (filtro_premium or filtro_velas or filtro_diverg or filtro_macd_combo or filtro_confluencia or filtro_emas or filtro_puntob):
        st.error("⚠️ Activa al menos un filtro de búsqueda.")
        st.stop()

    master_list = list(dict.fromkeys(
        ticker for idx_name in indices_seleccionados for ticker in UNIVERSO[idx_name]
    ))

    st.success(f"📡 **{len(master_list)} OBJETIVOS** · **{len(indices_seleccionados)} ÍNDICES** — ESCANEO EN PROCESO...")

    res_prem   = []
    res_velas  = []
    res_diverg = []
    res_macd        = []
    res_confluencia = []
    res_emas        = []
    res_puntob      = []

    progress_bar = st.progress(0)
    status_text  = st.empty()
    col_live1, col_live2, col_live3 = st.columns(3)
    ph_prem  = col_live1.empty()
    ph_velas = col_live2.empty()
    ph_div   = col_live3.empty()

    for i, ticker in enumerate(master_list):
        progress_bar.progress((i + 1) / len(master_list))
        status_text.text(f"🔎 {ticker}  [{i+1}/{len(master_list)}]")
        time.sleep(0.05)

        pack = procesar_datos(ticker, incluir_4h=(filtro_puntob and pb_4h))
        if pack is None:
            continue

        precio = round(float(pack['D'].iloc[-1]['Close']), 2)

        if filtro_premium:
            es_sup, txt, stop = super_buscador(pack)
            if es_sup:
                if ("BUY" in txt and dir_alcista) or ("SELL" in txt and dir_bajista):
                    res_prem.append({"Ticker": ticker, "Señal": txt, "Precio": precio, "Stop Ref": round(float(stop), 2)})
                    ph_prem.dataframe(pd.DataFrame(res_prem), use_container_width=True)

        if filtro_velas:
            for tf_key, tf_name in [('M', 'MENSUAL'), ('W', 'SEMANAL')]:
                for j in range(4):
                    es, t, k, s = check_vela_engano(pack[tf_key], idx=-1-j)
                    if es:
                        es_alc = "ALCISTA" in t
                        if (es_alc and dir_alcista) or (not es_alc and dir_bajista):
                            res_velas.append({
                                "Ticker": ticker, "TF": tf_name, "Señal": t,
                                "Antigüedad": f"Hace {j} {'Mes' if tf_key=='M' else 'Sem'}",
                                "Stoch K": round(k, 1), "Precio": precio
                            })
                            ph_velas.dataframe(pd.DataFrame(res_velas), use_container_width=True)
                        break

        if filtro_diverg:
            for tf_key, tf_name in [('D', 'DIARIO'), ('W', 'SEMANAL'), ('M', 'MENSUAL')]:
                es_div, tipo_div, duracion, antiguedad = check_divergencia(pack[tf_key], timeframe=tf_key)
                if es_div:
                    es_alc_div = "ALCISTA" in tipo_div
                    if (es_alc_div and dir_alcista) or (not es_alc_div and dir_bajista):
                        res_diverg.append({
                            "Ticker":     ticker,
                            "TF":         tf_name,
                            "Tipo":       tipo_div,
                            "Duración":   duracion,
                            "Formada":    antiguedad,
                            "Precio":     precio
                        })
                        ph_div.dataframe(pd.DataFrame(res_diverg), use_container_width=True)

        if filtro_macd_combo:
            estado_m = check_macd_estado(pack['M'])
            estado_w = check_macd_estado(pack['W'])
            estado_d = check_macd_estado(pack['D'])

            def cumple(seleccion, estado):
                if seleccion == "⚪ Cualquiera": return True
                if seleccion == "🟢 Alcista"   : return estado == 'alcista'
                if seleccion == "🔴 Bajista"   : return estado == 'bajista'
                return True

            if cumple(macd_m, estado_m) and cumple(macd_w, estado_w) and cumple(macd_d, estado_d):
                def icono(e): return "🟢" if e=='alcista' else ("🔴" if e=='bajista' else "⚪")
                res_macd.append({
                    "Ticker":   ticker,
                    "Mensual":  f"{icono(estado_m)} {estado_m.capitalize()}",
                    "Semanal":  f"{icono(estado_w)} {estado_w.capitalize()}",
                    "Diario":   f"{icono(estado_d)} {estado_d.capitalize()}",
                    "Precio":   precio
                })

        # ── CONFLUENCIA: Divergencia + Vela de Engaño mismo TF ──
        if filtro_confluencia:
            for tf_key, tf_name in [('W', 'SEMANAL'), ('M', 'MENSUAL')]:
                # Buscar vela de engaño en este TF
                for j in range(4):
                    es_vela, tipo_vela, k_vela, stop_vela = check_vela_engano(pack[tf_key], idx=-1-j)
                    if not es_vela:
                        continue
                    # Buscar divergencia en mismo TF con misma dirección
                    es_div, tipo_div, duracion, antiguedad = check_divergencia(pack[tf_key], timeframe=tf_key)
                    if not es_div:
                        break
                    # Verificar que apuntan en la misma dirección
                    vela_alc = "ALCISTA" in tipo_vela
                    div_alc  = "ALCISTA" in tipo_div
                    if vela_alc != div_alc:
                        break
                    # Filtro dirección global
                    if vela_alc and not dir_alcista: break
                    if not vela_alc and not dir_bajista: break

                    icono = "🚀" if vela_alc else "💣"
                    res_confluencia.append({
                        "Ticker":      ticker,
                        "TF":          tf_name,
                        "Dirección":   f"{'🟢 ALCISTA' if vela_alc else '🔴 BAJISTA'}",
                        "Señal":       f"{icono} DIV + VELA ENGAÑO",
                        "Div Fuerza":  tipo_div.split("(")[1].replace(")","") if "(" in tipo_div else "-",
                        "Div Dur.":    duracion,
                        "Vela Stoch":  round(k_vela, 1),
                        "Antigüedad":  f"Hace {j} {'Mes' if tf_key=='M' else 'Sem'}",
                        "Precio":      precio,
                        "Stop Ref":    round(float(stop_vela), 2)
                    })
                    break  # solo una confluencia por TF por ticker

        # ── CRUCE EMA 50/200 ──
        if filtro_emas:
            for tf_key, tf_name in [('D', 'DIARIO'), ('W', 'SEMANAL')]:
                es_cruce, tipo_cruce = check_cruce_emas(pack[tf_key], velas=4)
                if es_cruce:
                    es_golden = "GOLDEN" in tipo_cruce
                    if (es_golden and dir_alcista) or (not es_golden and dir_bajista):
                        res_emas.append({
                            "Ticker":  ticker,
                            "TF":      tf_name,
                            "Señal":   tipo_cruce,
                            "Precio":  precio
                        })

        # ── MÓDULO DE ARRANQUE — PUNTO B ──
        if filtro_puntob:
            tfs_pb = []
            if pb_4h and not pack['4H'].empty: tfs_pb.append(('4H', '4 HORAS'))
            if pb_d:  tfs_pb.append(('D', 'DIARIO'))
            if pb_w:  tfs_pb.append(('W', 'SEMANAL'))
            if pb_m:  tfs_pb.append(('M', 'MENSUAL'))

            for tf_key, tf_name in tfs_pb:
                df_tf = pack.get(tf_key)
                if df_tf is None or (hasattr(df_tf, 'empty') and df_tf.empty):
                    continue
                es_pb, tipo_pb, nivel_b, tp1, tp2, info = check_punto_b(df_tf, timeframe=tf_key)
                if es_pb:
                    es_bajista_pb = "BAJISTA" in tipo_pb
                    if (not es_bajista_pb and dir_alcista) or (es_bajista_pb and dir_bajista):
                        def velas_a_tiempo(v, tf):
                            if tf == "4H":
                                horas = v * 4
                                if horas < 24: return f"{horas}h"
                                dias = horas // 24
                                return f"{dias} dia{'s' if dias>1 else ''}"
                            elif tf == "D":
                                if v <= 1:  return "Hoy"
                                if v < 5:   return f"{v} dias"
                                sem = v // 5
                                return f"{sem} semana{'s' if sem>1 else ''}"
                            elif tf == "W":
                                if v <= 1:  return "Esta semana"
                                if v < 4:   return f"{v} semanas"
                                mes = round(v * 7 / 30)
                                return f"{mes} mes{'es' if mes>1 else ''}"
                            elif tf == "M":
                                if v <= 1: return "Este mes"
                                return f"{v} meses"
                            return f"{v} velas"

                        duracion_txt = velas_a_tiempo(info["duracion_velas"], tf_key)
                        desde_c_txt  = velas_a_tiempo(info["velas_desde_c"],  tf_key)
                        if info["estado_b"] == "✅ ROTO" and info["velas_ruptura"] > 0:
                            roto_hace_txt = velas_a_tiempo(info["velas_ruptura"], tf_key)
                        elif info["estado_b"] == "✅ ROTO":
                            roto_hace_txt = "Hoy"
                        else:
                            roto_hace_txt = "—"

                        res_puntob.append({
                            "Ticker":        ticker,
                            "TF":            tf_name,
                            "Tipo":          tipo_pb,
                            "Estado B":      info["estado_b"],
                            "Nivel B":       info["nivel_b"],
                            "Precio A":      info["precio_a"],
                            "Precio C":      info["precio_c"],
                            "TP1 (161.8%)":  tp1,
                            "TP2 (200%)":    tp2,
                            "Dur. modulo":   duracion_txt,
                            "Desde C":       desde_c_txt,
                            "Roto hace":     roto_hace_txt,
                            "Precio":        precio
                        })

    ph_prem.empty(); ph_velas.empty(); ph_div.empty()
    progress_bar.empty()
    status_text.success("✅ ESCANEO COMPLETADO.")
    st.balloons()

    st.markdown("---")
    m1, m2, m3, m4, m5, m6, m7, m8 = st.columns(8)
    m1.metric("🎯 Escaneados",       len(master_list))
    m2.metric("💎 Premium",          len(res_prem))
    m3.metric("🕯️ Velas Engaño",    len(res_velas))
    m4.metric("📐 Divergencias",     len(res_diverg))
    m5.metric("📡 MACD Combo",       len(res_macd))
    m6.metric("💥 Confluencia",      len(res_confluencia))
    m7.metric("📈 EMA Cross",        len(res_emas))
    m8.metric("🔵 Punto B",          len(res_puntob))
    st.markdown("---")

    tab_labels = []
    if filtro_premium:    tab_labels.append(f"💎 PREMIUM ({len(res_prem)})")
    if filtro_velas:      tab_labels.append(f"🕯️ VELAS ({len(res_velas)})")
    if filtro_diverg:     tab_labels.append(f"📐 DIVERGENCIAS ({len(res_diverg)})")
    if filtro_macd_combo:   tab_labels.append(f"📡 MACD COMBO ({len(res_macd)})")
    if filtro_confluencia:  tab_labels.append(f"💥 CONFLUENCIA ({len(res_confluencia)})")
    if filtro_emas:         tab_labels.append(f"📈 EMA CROSS ({len(res_emas)})")
    if filtro_puntob:       tab_labels.append(f"🔵 PUNTO B ({len(res_puntob)})")

    tabs = st.tabs(tab_labels)
    tab_idx = 0

    if filtro_premium:
        with tabs[tab_idx]:
            if res_prem:
                df_out = pd.DataFrame(res_prem)
                st.dataframe(df_out, use_container_width=True)
                st.download_button("⬇️ Exportar CSV", df_out.to_csv(index=False).encode(), "premium.csv", "text/csv")
            else:
                st.warning("Sin entradas Premium hoy. Mantener disciplina.")
        tab_idx += 1

    if filtro_velas:
        with tabs[tab_idx]:
            if res_velas:
                df_out = pd.DataFrame(res_velas)
                alc = df_out[df_out['Señal'].str.contains("ALCISTA")]
                baj = df_out[df_out['Señal'].str.contains("BAJISTA")]
                if not alc.empty:
                    st.markdown("#### 🟢 ALCISTAS"); st.dataframe(alc, use_container_width=True)
                if not baj.empty:
                    st.markdown("#### 🔴 BAJISTAS"); st.dataframe(baj, use_container_width=True)
                st.download_button("⬇️ Exportar CSV", df_out.to_csv(index=False).encode(), "velas.csv", "text/csv")
            else:
                st.info("Sin velas de engaño detectadas.")
        tab_idx += 1

    if filtro_diverg:
        with tabs[tab_idx]:
            if res_diverg:
                df_out = pd.DataFrame(res_diverg)
                alc = df_out[df_out['Tipo'].str.contains("ALCISTA")]
                baj = df_out[df_out['Tipo'].str.contains("BAJISTA")]
                if not alc.empty:
                    st.markdown("#### 📈 ALCISTAS"); st.dataframe(alc, use_container_width=True)
                if not baj.empty:
                    st.markdown("#### 📉 BAJISTAS"); st.dataframe(baj, use_container_width=True)
                st.download_button("⬇️ Exportar CSV", df_out.to_csv(index=False).encode(), "divergencias.csv", "text/csv")
            else:
                st.info("Sin divergencias detectadas.")
        tab_idx += 1

    if filtro_macd_combo:
        with tabs[tab_idx]:
            if res_macd:
                df_out = pd.DataFrame(res_macd)
                st.markdown("#### 📡 RESULTADOS RADAR MACD")
                st.dataframe(df_out, use_container_width=True)
                st.download_button("⬇️ Exportar CSV", df_out.to_csv(index=False).encode(), "macd_combo.csv", "text/csv")
            else:
                st.info("Ningún activo cumple la combinación MACD seleccionada.")
        tab_idx += 1

    if filtro_confluencia:
        with tabs[tab_idx]:
            if res_confluencia:
                df_out = pd.DataFrame(res_confluencia)
                alc = df_out[df_out['Dirección'].str.contains("ALCISTA")]
                baj = df_out[df_out['Dirección'].str.contains("BAJISTA")]
                if not alc.empty:
                    st.markdown("#### 🚀 CONFLUENCIAS ALCISTAS")
                    st.dataframe(alc, use_container_width=True)
                if not baj.empty:
                    st.markdown("#### 💣 CONFLUENCIAS BAJISTAS")
                    st.dataframe(baj, use_container_width=True)
                st.download_button("⬇️ Exportar CSV", df_out.to_csv(index=False).encode(), "confluencia.csv", "text/csv")
            else:
                st.info("No se han detectado confluencias Divergencia + Vela de Engaño.")
        tab_idx += 1

    if filtro_emas:
        with tabs[tab_idx]:
            if res_emas:
                df_out = pd.DataFrame(res_emas)
                golden = df_out[df_out['Señal'].str.contains("GOLDEN")]
                death  = df_out[df_out['Señal'].str.contains("DEATH")]
                if not golden.empty:
                    st.markdown("#### ✨ GOLDEN CROSS — EMA50 cruza sobre EMA200")
                    st.dataframe(golden, use_container_width=True)
                if not death.empty:
                    st.markdown("#### 💀 DEATH CROSS — EMA50 cruza bajo EMA200")
                    st.dataframe(death, use_container_width=True)
                st.download_button("⬇️ Exportar CSV", df_out.to_csv(index=False).encode(), "ema_cross.csv", "text/csv")
            else:
                st.info("No se han detectado cruces de EMA50/200 recientes.")
        tab_idx += 1

    if filtro_puntob:
        with tabs[tab_idx]:
            if res_puntob:
                df_out = pd.DataFrame(res_puntob)
                buenas = df_out[df_out['Tipo'].str.contains("BUENA")]
                malas  = df_out[df_out['Tipo'].str.contains("MALA")]
                alc_buenas = df_out[df_out['Tipo'].str.contains("BUENA") & ~df_out['Tipo'].str.contains("BAJISTA")]
                alc_malas  = df_out[df_out['Tipo'].str.contains("MALA")  & ~df_out['Tipo'].str.contains("BAJISTA")]
                baj_buenas = df_out[df_out['Tipo'].str.contains("BUENA OSCILACIÓN BAJISTA|BUENA OSC. BAJISTA")]
                baj_malas  = df_out[df_out['Tipo'].str.contains("MALA OSCILACIÓN BAJISTA|MALA OSC. BAJISTA")]

                if not alc_buenas.empty:
                    st.markdown("#### 🟢 BUENA OSCILACIÓN ALCISTA — C < A")
                    st.dataframe(alc_buenas, use_container_width=True)
                if not alc_malas.empty:
                    st.markdown("#### 🟡 MALA OSCILACIÓN ALCISTA — C > A")
                    st.dataframe(alc_malas, use_container_width=True)
                if not baj_buenas.empty:
                    st.markdown("#### 🔴 BUENA OSCILACIÓN BAJISTA — C > A")
                    st.dataframe(baj_buenas, use_container_width=True)
                if not baj_malas.empty:
                    st.markdown("#### 🟠 MALA OSCILACIÓN BAJISTA — C < A")
                    st.dataframe(baj_malas, use_container_width=True)
                st.download_button("⬇️ Exportar CSV", df_out.to_csv(index=False).encode(), "punto_b.csv", "text/csv")
            else:
                st.info("No se han detectado módulos de arranque válidos.")

else:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("📊", "ÍNDICES", "17 mercados"),
        ("🎯", "TICKERS", f"~{sum(len(v) for v in UNIVERSO.values())} activos"),
        ("🌍", "COBERTURA", "USA · EU · UK · JP"),
        ("⚡", "ETFs", "Sectores · Temáticos · Apalancados"),
    ]
    for col, (icon, label, val) in zip([c1,c2,c3,c4], stats):
        col.markdown(f"""
        <div style='background:#0d1117; border:1px solid #1e3a2f; border-radius:8px;
                    padding:16px; text-align:center;'>
            <div style='font-size:1.8rem;'>{icon}</div>
            <div style='font-family:Orbitron; color:#00e676; font-size:11px;
                        letter-spacing:2px; margin:4px 0;'>{label}</div>
            <div style='font-family:Share Tech Mono; color:#c9d1d9; font-size:13px;'>{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    bloques = [
        ("💎 PREMIUM", "Confluencia M + W + D\nMACD estricto multi-timeframe\n+ Vela de engaño semanal"),
        ("🕯️ VELAS ENGAÑO", "Barrido de mínimos/máximos\nRecuperación > 50% vela\nEstocástico extremo (<20 / >80)"),
        ("📐 DIVERGENCIAS", "Precio vs Momentum MACD\nVentana de 10 velas\nDisponible en D / W / M"),
    ]
    for col, (titulo, desc) in zip([c1,c2,c3], bloques):
        col.markdown(f"""
        <div style='background:#0d1117; border:1px solid #1e3a2f; border-radius:8px; padding:16px;'>
            <div style='font-family:Orbitron; color:#00e676; font-size:12px;
                        margin-bottom:10px; letter-spacing:1px;'>{titulo}</div>
            <div style='font-family:Share Tech Mono; color:#8b949e; font-size:11px;
                        line-height:1.9; white-space:pre-line;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; font-family:Share Tech Mono; color:#2a3f2a;
                font-size:12px; letter-spacing:3px;'>
        ← SELECCIONA ÍNDICES Y FILTROS · PULSA LANZAR RADAR →
    </div>
    """, unsafe_allow_html=True)

















