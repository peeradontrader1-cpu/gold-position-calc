import streamlit as st

# --- 1. CONFIG & THEME (FORMAL ALL-BLACK) ---
st.set_page_config(page_title="Gold Risk Manager", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; font-weight: 200; letter-spacing: 1px; }
    .stNumberInput input { background-color: #121212 !important; color: #FFFFFF !important; border: 1px solid #333333 !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #121212 !important; border: 1px solid #333333 !important; }
    div[data-testid="stMetric"] { background-color: #0A0A0A; border-left: 3px solid #FFFFFF; padding: 15px; }
    .stAlert { background-color: #111111 !important; border: 1px solid #333333 !important; color: white !important; }
    hr { border-top: 1px solid #222222; }
</style>
""", unsafe_allow_html=True)

st.title("GOLD POSITION SIZING")
st.markdown("<p style='color:#666666;'>SYSTEM SPECIFICATION: GC & MGC</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- 2. INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("ACCOUNT & RISK")
    balance = st.number_input("Account Balance ($)", value=50519.0, step=100.0)
    
    risk_mode = st.radio("Risk Calculation Mode", ["Fixed Cash ($)", "Percentage (%)"])
    
    if risk_mode == "Fixed Cash ($)":
        final_risk_usd = st.number_input("Risk Amount ($)", value=100.0, step=10.0)
    else:
        risk_pct = st.number_input("Risk Percentage (%)", value=1.0, step=0.1)
        final_risk_usd = balance * (risk_pct / 100)
        st.info(f"Calculated Risk: ${final_risk_usd:,.2f}")

with col2:
    st.subheader("TRADE SETUP")
    symbol = st.selectbox("Contract Type", ["MGC (Micro)", "GC (Standard)"])
    entry_p = st.number_input("Entry Price", value=4750.00, format="%.2f")
    sl_p = st.number_input("Stop Loss Price", value=4755.00, format="%.2f")
    tp_p = st.number_input("Take Profit Price", value=4725.00, format="%.2f")

# --- 3. CALCULATION ENGINE (CORRECTED LOGIC) ---
points_sl = abs(entry_p - sl_p)
points_tp = abs(entry_p - tp_p)

# Multiplier Logic: MGC = 10, GC = 100
if "MGC" in symbol:
    multiplier = 10
else:
    multiplier = 100

if points_sl > 0:
    # คำนวณความเสี่ยงต่อ 1 คอนแทรค: ระยะทาง * ตัวคูณ
    risk_per_con = points_sl * multiplier
    
    # จำนวนคอนแทรค: เงินที่ยอมเสีย / ความเสี่ยงต่อคอนแทรค
    contracts = final_risk_usd / risk_per_con
    
    # RR Ratio
    rr_ratio = points_tp / points_sl

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- 4. OUTPUT ---
    st.subheader("EXECUTION DATA")
    res1, res2, res3 = st.columns(3)
    res1.metric("SL POINTS", f"{points_sl:.2f}")
    res2.metric("RR RATIO", f"1:{rr_ratio:.2f}")
    res3.metric("SIZE (CONS)", f"{contracts:.2f}")

    # Topstep Guard (แจ้งเตือน 5 คอนแทรค)
    if contracts > 5:
        st.error(f"❌ VIOLATION: {contracts:.2f} contracts exceeds Topstep 5-con limit.")
    else:
        st.success(f"✅ COMPLIANT: Open {contracts:.2f} contracts.")
        
    st.markdown(f"<p style='color:#555;'>* {symbol} Value: ${multiplier} per 1.00 Point change</p>", unsafe_allow_html=True)
else:
    st.warning("Define entry and stop loss prices.")
