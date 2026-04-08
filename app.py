import streamlit as st

# --- 1. MODERN & LUXURY UI CONFIG ---
st.set_page_config(page_title="Gold Risk Professional", layout="centered")

st.markdown("""
<style>
    /* พื้นหลังดำลึกและฟอนต์สะอาดตา */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    
    /* หัวข้อเน้นความเฉียบคม */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }

    /* ตกแต่ง Input ให้ดูทันสมัย (Border-radius มากขึ้นและขอบจางๆ) */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0F0F0F !important;
        color: #FFFFFF !important;
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    /* กล่อง Metric แสดงผลลัพธ์ */
    div[data-testid="stMetric"] {
        background-color: #0A0A0A;
        border: 1px solid #1A1A1A;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* ปรับแต่งส่วน Error และ Success ให้ดู Minimal */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
    }

    /* กรอบเล็กๆ สำหรับอธิบายวิธีคำนวณด้านล่าง */
    .guide-box {
        background-color: #0A0A0A;
        border: 1px solid #1A1A1A;
        padding: 20px;
        border-radius: 12px;
        font-size: 14px;
        color: #888888;
        line-height: 1.6;
    }
    
    hr { border-top: 1px solid #1A1A1A; }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.title("🥇 Gold Risk Management")
st.markdown("<p style='color:#666666;'>PROFESSIONAL EXECUTION TOOL</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- 3. INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Account & Risk")
    balance = st.number_input("Account Balance ($)", value=50519.0)
    risk_mode = st.radio("Risk Mode", ["Fixed Cash ($)", "Percentage (%)"])
    
    if risk_mode == "Fixed Cash ($)":
        final_risk_usd = st.number_input("Risk Amount ($)", value=100.0)
    else:
        risk_pct = st.number_input("Risk (%)", value=1.0, step=0.1)
        final_risk_usd = balance * (risk_pct / 100)
        st.caption(f"Calculated Risk: ${final_risk_usd:,.2f}")

with col2:
    st.markdown("### Trade Setup")
    symbol = st.selectbox("Contract Type", ["MGC (Micro)", "GC (Standard)"])
    entry_p = st.number_input("Entry Price", value=4750.00, format="%.2f")
    sl_p = st.number_input("Stop Loss Price", value=4755.00, format="%.2f")
    tp_p = st.number_input("Take Profit Price", value=4725.00, format="%.2f")

# --- 4. CALCULATION ENGINE ---
points_sl = abs(entry_p - sl_p)
points_tp = abs(entry_p - tp_p)
multiplier = 10 if "MGC" in symbol else 100

if points_sl > 0:
    risk_per_con = points_sl * multiplier
    contracts = final_risk_usd / risk_per_con
    rr_ratio = points_tp / points_sl if points_sl > 0 else 0

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- 5. EXECUTION DATA ---
    res1, res2, res3 = st.columns(3)
    res1.metric("SL DISTANCE", f"{points_sl:.2f} Pts")
    res2.metric("RR RATIO", f"1:{rr_ratio:.2f}")
    res3.metric("POSITION SIZE", f"{contracts:.2f}")

    # --- 6. VALIDATION LOGIC (เพิ่มเงื่อนไขตามคำสั่ง) ---
    if contracts > 5:
        st.error(f"⚠️ VIOLATION: {contracts:.2f} contracts exceeds Topstep 5-con limit.")
    elif contracts < 1.0:
        # ขึ้นตัวสีแดงหากคำนวณได้น้อยกว่า 1 คอนแทรค
        st.error(f"⚠️ INSUFFICIENT SIZE: {contracts:.2f} contracts (Min 1.00 contract required to execute).")
    else:
        st.success(f"✅ COMPLIANT: Open {contracts:.2f} contracts.")

else:
    st.warning("Define entry and stop loss prices.")

# --- 7. REFERENCE GUIDE (ส่วนที่เพิ่มใหม่ด้านล่าง) ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### 📘 Contract Specifications & Calculation")
st.markdown(f"""
<div class="guide-box">
    <b>สูตรการคำนวณ:</b><br>
    จำนวนสัญญา = Risk ($) ÷ (ระยะ SL x Multiplier)<br><br>
    <b>รายละเอียดสัญญา (Contract Details):</b><br>
    • <b>GC (Standard Gold):</b> 1 Point = $100 | ตัวคูณ (Multiplier) คือ 100<br>
    • <b>MGC (Micro Gold):</b> 1 Point = $10 | ตัวคูณ (Multiplier) คือ 10<br><br>
    <i>ตัวอย่าง: หากใช้ MGC และ SL 5 จุด จะมีความเสี่ยงต่อสัญญาคือ 5 x 10 = $50 ต่อ 1 สัญญา</i>
</div>
""", unsafe_allow_html=True)
