import streamlit as st

# ==========================================
# 1. UI & DESIGN (FORMAL MINIMALIST)
# ==========================================
st.set_page_config(page_title="Gold Risk Manager", layout="centered")

# Custom CSS สำหรับสไตล์ All-Black และการจัดการ Layout
st.markdown("""
<style>
    /* พื้นหลังดำสนิทและตัวอักษรขาว */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    /* ปรับแต่งหัวข้อ (Header) ให้ดูเป็นทางการ */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 200;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* ตกแต่งช่อง Input ให้กลืนกับพื้นหลัง */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #121212 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
    }

    /* ปรับแต่งปุ่มและ Metric */
    div[data-testid="stMetric"] {
        background-color: #0A0A0A;
        border: 1px solid #222222;
        padding: 20px;
        border-radius: 8px;
    }

    /* เส้นแบ่งที่เรียบเนียน */
    hr {
        border-top: 1px solid #222222;
    }

    /* การแจ้งเตือน */
    .stAlert {
        background-color: #000000 !important;
        border: 1px solid #444444 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. APP HEADER
# ==========================================
st.title("🥇 Gold Position Sizing")
st.markdown("<p style='color:#888888; font-size:14px;'>STRICT RISK MANAGEMENT SYSTEM | TOPSTEP COMPLIANCE</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 3. INPUT SECTION (ACCOUNT & TRADE)
# ==========================================
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Account & Risk")
        balance = st.number_input("Account Balance ($)", value=50000.0, step=1000.0)
        risk_usd = st.number_input("Risk Amount ($)", value=500.0, step=10.0)
        # คำนวณ % จากยอดเงินจริงแบบ Real-time
        current_risk_pct = (risk_usd / balance) * 100 if balance > 0 else 0
        st.markdown(f"<p style='color:#666666;'>Current Risk: {current_risk_pct:.2f}% of Balance</p>", unsafe_allow_html=True)

    with col2:
        st.subheader("Trade Specs")
        symbol = st.selectbox("Contract Type", ["GC (Standard)", "MGC (Micro)"])
        entry_p = st.number_input("Entry Price", value=2000.00, format="%.2f", step=0.10)
        sl_p = st.number_input("Stop Loss Price", value=1995.00, format="%.2f", step=0.10)
        tp_p = st.number_input("Take Profit Price", value=2010.00, format="%.2f", step=0.10)

# ==========================================
# 4. CALCULATION ENGINE
# ==========================================
# 1. หาระยะทาง
dist_sl = abs(entry_p - sl_p)
dist_tp = abs(entry_p - tp_p)

# 2. คำนวณ RR Ratio
rr_ratio = dist_tp / dist_sl if dist_sl > 0 else 0

# 3. กำหนด Multiplier (หัวใจสำคัญที่คุณย้ำ)
# GC: 1 point = $100 | MGC: 1 point = $10
multiplier = 100 if "GC" in symbol else 10

if dist_sl > 0:
    # 4. คำนวณจำนวนสัญญา: Risk ($) / (ระยะจุด * ตัวคูณ)
    # สูตร: $500 / (5 points * $100) = 1 Contract (สำหรับ GC)
    contracts = risk_usd / (dist_sl * multiplier)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ==========================================
    # 5. OUTPUT & NOTIFICATION
    # ==========================================
    st.subheader("Analysis Result")
    res1, res2, res3 = st.columns(3)
    
    res1.metric("SL POINTS", f"{dist_sl:.2f}")
    res2.metric("RR RATIO", f"1:{rr_ratio:.2f}")
    res3.metric("CONTRACTS", f"{contracts:.2f}")

    # Topstep Guard: แจ้งเตือนกฎ 5 คอนแทรค
    if contracts > 5:
        st.error(f"❌ VIOLATION: {contracts:.2f} contracts exceeds the Topstep 5-contract limit.")
    else:
        st.success(f"✅ COMPLIANT: {contracts:.2f} contracts is within safety limits.")
    
    # คำอธิบายเพิ่มเติม
    st.info(f"Summary: {symbol} at {dist_sl} pts SL costs ${(dist_sl * multiplier):.2f} per contract.")

else:
    st.warning("Please adjust Entry and Stop Loss prices to calculate.")
