import streamlit as st

# --- 1. LUXURY UI CONFIG ---
st.set_page_config(page_title="Gold Terminal Pro", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Header สไตล์ Old Money */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 700;
        letter-spacing: 1px;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* ตกแต่ง Input */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
        border: 1px solid #222222 !important;
        border-radius: 4px !important;
    }

    /* กล่อง Metric */
    div[data-testid="stMetric"] {
        background-color: #050505;
        border: 1px solid #1A1A1A;
        padding: 20px;
        border-radius: 4px;
    }

    /* RR Bar Visualization */
    .rr-bar-container {
        width: 100%;
        height: 12px;
        background-color: #1A1A1A;
        border-radius: 6px;
        margin: 20px 0;
        display: flex;
        overflow: hidden;
    }

    /* Guide Box */
    .guide-box {
        background-color: #050505;
        border: 1px solid #111111;
        padding: 20px;
        border-radius: 8px;
        font-size: 13px;
        color: #666666;
    }
    
    /* Animation สำหรับ Error */
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .violation-text { color: #FF4B4B; animation: blink 2s infinite; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER & RESET ---
st.markdown('<p class="main-title">GOLD TERMINAL</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#444; letter-spacing:3px; font-size:12px;'>RISK MANAGEMENT & EXECUTION</p>", unsafe_allow_html=True)

if st.button("RESET TERMINAL"):
    st.rerun()

st.markdown("<hr style='border-top: 1px solid #111;'>", unsafe_allow_html=True)

# --- 3. INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ACCOUNT STATUS")
    balance = st.number_input("Current Equity ($)", value=50519.0)
    daily_loss = st.number_input("Realized Daily Loss ($)", value=0.0, help="ยอดที่ขาดทุนสะสมในวันนี้")
    
    risk_mode = st.radio("Risk Method", ["Fixed Cash ($)", "Percentage (%)"])
    if risk_mode == "Fixed Cash ($)":
        final_risk_usd = st.number_input("Risk per Trade ($)", value=100.0)
    else:
        risk_pct = st.number_input("Risk per Trade (%)", value=1.0, step=0.1)
        final_risk_usd = balance * (risk_pct / 100)
    
    # Check Daily Loss Limit (สมมติเกณฑ์ปลอดภัยที่ 3% ของพอร์ต)
    max_daily = balance * 0.03
    if daily_loss >= max_daily:
        st.warning(f"⚠️ Daily Loss Limit Alert: You have reached 3% loss limit (${max_daily:.2f})")

with col2:
    st.markdown("### TRADE PARAMETERS")
    symbol = st.selectbox("Instrument", ["MGC (Micro)", "GC (Standard)"])
    entry_p = st.number_input("Entry", value=4750.00, format="%.2f")
    sl_p = st.number_input("Stop Loss", value=4755.00, format="%.2f")
    tp_p = st.number_input("Take Profit", value=4725.00, format="%.2f")

# --- 4. CALCULATION ---
dist_sl = abs(entry_p - sl_p)
dist_tp = abs(entry_p - tp_p)
multiplier = 10 if "MGC" in symbol else 100

if dist_sl > 0:
    risk_per_con = dist_sl * multiplier
    contracts = final_risk_usd / risk_per_con
    rr_ratio = dist_tp / dist_sl
    
    st.markdown("<hr style='border-top: 1px solid #111;'>", unsafe_allow_html=True)
    
    # --- 5. VISUAL RR BAR ---
    total_dist = dist_sl + dist_tp
    sl_weight = (dist_sl / total_dist) * 100
    tp_weight = (dist_tp / total_dist) * 100
    
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; font-size: 10px; color: #444;'>
        <span>STOP LOSS ({dist_sl:.2f})</span>
        <span>TAKE PROFIT ({dist_tp:.2f})</span>
    </div>
    <div class="rr-bar-container">
        <div style="width: {sl_weight}%; background-color: #7f1d1d;"></div>
        <div style="width: {tp_weight}%; background-color: #064e3b;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 6. OUTPUT METRICS ---
    res1, res2, res3 = st.columns(3)
    res1.metric("DISTANCE", f"{dist_sl:.2f}")
    res2.metric("REWARD RATIO", f"1:{rr_ratio:.2f}")
    res3.metric("SIZE (CONS)", f"{contracts:.2f}")

    # --- 7. SAFETY VALIDATION ---
    if contracts > 5:
        st.markdown(f'<p class="violation-text">⚠️ EXCEEDS TOPSTEP LIMIT: {contracts:.2f} CONS</p>', unsafe_allow_html=True)
    elif contracts < 1.0:
        st.markdown(f'<p class="violation-text">⚠️ INSUFFICIENT SIZE: {contracts:.2f} CONS (MIN 1.00)</p>', unsafe_allow_html=True)
    else:
        st.success(f"PROCEED: {contracts:.2f} Contracts compliant.")

else:
    st.warning("Awaiting valid entry and stop loss prices.")

# --- 8. REFERENCE ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="guide-box">
    <b>SPECIFICATION REFERENCE</b><br>
    • {symbol} Multiplier: {multiplier}x<br>
    • Risk per Contract: ${dist_sl * multiplier:.2f}<br>
    • Formula: Risk Amount / (Distance * Multiplier)
</div>
""", unsafe_allow_html=True)
