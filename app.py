import streamlit as st

# --- 1. SETTING & THEME (FORMAL ALL-BLACK) ---
st.set_page_config(page_title="Professional Gold Calc", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; font-weight: 200; letter-spacing: 1px; }
    .stNumberInput input { background-color: #121212 !important; color: #FFFFFF !important; border: 1px solid #333333 !important; }
    div[data-testid="stMetric"] { background-color: #0A0A0A; border-left: 3px solid #FFFFFF; padding: 15px; }
    .stAlert { background-color: #111111 !important; border: 1px solid #333333 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("GOLD POSITION SIZING")
st.markdown("<hr>", unsafe_allow_html=True)

# --- 2. INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("ACCOUNT & RISK")
    balance = st.number_input("Account Balance ($)", value=50000.0, step=1000.0)
    # ให้เลือกว่าจะใช้ Risk แบบไหนเป็นหลัก
    risk_mode = st.radio("Risk Calculation Mode", ["Fixed Cash ($)", "Percentage (%)"])
    
    if risk_mode == "Fixed Cash ($)":
        final_risk_usd = st.number_input("Risk Amount ($)", value=500.0, step=10.0)
    else:
        risk_pct = st.number_input("Risk Percentage (%)", value=1.0, step=0.1)
        final_risk_usd = balance * (risk_pct / 100)
        st.info(f"Calculated Risk: ${final_risk_usd:,.2f}")

with col2:
    st.subheader("TRADE SETUP")
    symbol = st.selectbox("Contract Type", ["GC (Standard)", "MGC (Micro)"])
    entry_p = st.number_input("Entry Price", value=2000.00, format="%.2f")
    sl_p = st.number_input("Stop Loss Price", value=1995.00, format="%.2f")
    tp_p = st.number_input("Take Profit Price", value=2010.00, format="%.2f")

# --- 3. CALCULATION ENGINE (CORRECTED) ---
points_sl = abs(entry_p - sl_p)
points_tp = abs(entry_p - tp_p)
multiplier = 100 if "GC" in symbol else 10

if points_sl > 0:
    # คำนวณความเสี่ยงต่อ 1 คอนแทรค (Risk Per Contract)
    # เช่น GC: 5 points * 100 = $500
    risk_per_con = points_sl * multiplier
    
    # คำนวณจำนวนสัญญา (Contracts)
    # เช่น $500 (Risk USD) / $500 (Risk Per Con) = 1 Contract
    contracts = final_risk_usd / risk_per_con
    
    rr_ratio = points_tp / points_sl

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- 4. OUTPUT ---
    st.subheader("EXECUTION DATA")
    res1, res2, res3 = st.columns(3)
    res1.metric("SL POINTS", f"{points_sl:.2f}")
    res2.metric("RR RATIO", f"1:{rr_ratio:.2f}")
    res3.metric("SIZE (CONS)", f"{contracts:.2f}")

    # Topstep Guard
    if contracts > 5:
        st.error(f"❌ VIOLATION: {contracts:.2f} contracts exceeds Topstep 5-con limit.")
    elif contracts <= 0:
        st.warning("Invalid Position Size.")
    else:
        st.success(f"✅ COMPLIANT: Open {contracts:.2f} contracts.")
        
    st.markdown(f"<p style='color:#555;'>* 1 Contract of {symbol} = ${multiplier} per 1 Point change</p>", unsafe_allow_html=True)
else:
    st.warning("Stop Loss distance cannot be zero.")
