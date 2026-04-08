import streamlit as st
import feedparser
import pandas as pd

# --- 1. LUXURY UI CONFIG (OLD MONEY ALL-BLACK) ---
st.set_page_config(page_title="Gold Terminal Pro", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Header สไตล์เรียบหรู */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 40px;
        font-weight: 700;
        text-align: center;
        letter-spacing: 1px;
        margin-bottom: 0px;
        color: #FFFFFF;
    }
    
    /* ตกแต่ง Input & Selectbox ให้ดูเนี๊ยบ */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
        border: 1px solid #222222 !important;
        border-radius: 4px !important;
    }

    /* Metric Display */
    div[data-testid="stMetric"] {
        background-color: #050505;
        border: 1px solid #1A1A1A;
        padding: 20px;
        border-radius: 4px;
    }

    /* ส่วนตารางข่าว */
    .stDataFrame {
        border: 1px solid #1A1A1A !important;
    }

    /* Guide Box ด้านล่าง */
    .guide-box {
        background-color: #050505;
        border: 1px solid #111111;
        padding: 20px;
        border-radius: 8px;
        font-size: 13px;
        color: #666666;
        line-height: 1.6;
    }
    
    hr { border-top: 1px solid #1A1A1A; }
    
    /* บังคับสีปุ่ม Reset */
    .stButton button {
        background-color: #0A0A0A;
        color: #666;
        border: 1px solid #222;
        width: 100%;
        border-radius: 4px;
    }
    .stButton button:hover {
        border-color: #444;
        color: #FFF;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER & RESET FUNCTION ---
st.markdown('<p class="main-title">GOLD TERMINAL</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#444; letter-spacing:3px; font-size:10px; margin-bottom:20px;'>POSITION SIZING & RISK CONTROL</p>", unsafe_allow_html=True)

if st.button("RESET SYSTEM"):
    st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# --- 3. INPUT SECTION (บัญชีและความเสี่ยง) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ACCOUNT & RISK")
    balance = st.number_input("Account Balance ($)", value=50519.0)
    risk_mode = st.radio("Risk Method", ["Fixed Cash ($)", "Percentage (%)"])
    
    if risk_mode == "Fixed Cash ($)":
        final_risk_usd = st.number_input("Risk Amount ($)", value=100.0)
    else:
        risk_pct = st.number_input("Risk (%)", value=1.0, step=0.1)
        final_risk_usd = balance * (risk_pct / 100)
        st.caption(f"Calculated Risk: ${final_risk_usd:,.2f}")

with col2:
    st.markdown("### TRADE SETUP")
    symbol = st.selectbox("Instrument", ["MGC (Micro)", "GC (Standard)"])
    entry_p = st.number_input("Entry Price", value=4750.00, format="%.2f")
    sl_p = st.number_input("Stop Loss Price", value=4755.00, format="%.2f")
    tp_p = st.number_input("Take Profit Price", value=4725.00, format="%.2f")

# --- 4. CALCULATION ENGINE (ตรรกะห้ามพลาด) ---
dist_sl = abs(entry_p - sl_p)
dist_tp = abs(entry_p - tp_p)

# Multiplier: MGC = 10, GC = 100
multiplier = 10 if "MGC" in symbol else 100

if dist_sl > 0:
    # คำนวณความเสี่ยงต่อ 1 คอนแทรค
    risk_per_con = dist_sl * multiplier
    # คำนวณจำนวนสัญญา
    contracts = final_risk_usd / risk_per_con
    # คำนวณ RR
    rr_ratio = dist_tp / dist_sl if dist_sl > 0 else 0
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- 5. OUTPUT METRICS ---
    res1, res2, res3 = st.columns(3)
    res1.metric("SL DISTANCE", f"{dist_sl:.2f} Pts")
    res2.metric("RR RATIO", f"1:{rr_ratio:.2f}")
    res3.metric("SIZE (CONS)", f"{contracts:.2f}")

    # --- 6. SAFETY GUARD (ระบบตัวแดงแจ้งเตือน) ---
    if contracts > 5.001: # เผื่อเศษทศนิยมเล็กน้อย
        st.error(f"❌ VIOLATION: {contracts:.2f} contracts exceeds Topstep 5-con limit.")
    elif contracts < 1.0:
        st.error(f"⚠️ INSUFFICIENT SIZE: {contracts:.2f} contracts (Min 1.00 required).")
    else:
        st.success(f"✅ COMPLIANT: Open {contracts:.2f} contracts.")

else:
    st.warning("Please define a valid Stop Loss distance.")

# --- 7. REFERENCE GUIDE (ส่วนอธิบายท้ายเครื่องมือ) ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="guide-box">
    <b>SPECIFICATION REFERENCE</b><br>
    • {symbol} Multiplier: {multiplier}x | Risk per Contract: ${dist_sl * multiplier:.2f}<br>
    • Formula: Risk Amount / (Distance * Multiplier)<br>
    • 1.00 Point of {symbol} = ${multiplier}.00
</div>
""", unsafe_allow_html=True)

# --- 8. ECONOMIC CALENDAR (ส่วนข่าว USD) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 📅 Market Radar (USD Events)")

def get_market_news():
    try:
        # ดึง RSS จาก Forex Factory
        feed = feedparser.parse("https://www.forexfactory.com/ff_calendar_thisweek.xml")
        news_data = []
        for entry in feed.entries:
            if entry.get('currency') == 'USD':
                news_data.append({
                    "Event": entry.title,
                    "Impact": entry.get('impact', 'N/A')
                })
        return pd.DataFrame(news_data).head(10)
    except Exception:
        return pd.DataFrame(columns=["Event", "Impact"])

with st.spinner("Fetching market data..."):
    df_news = get_market_news()
    if not df_news.empty:
        # แสดงตารางแบบ Minimalist
        st.dataframe(df_news, use_container_width=True, hide_index=True)
    else:
        st.caption("No upcoming USD events found or feed unavailable.")

st.markdown("<p style='font-size:10px; color:#333; text-align:center;'>Professional Position Sizer v2.0</p>", unsafe_allow_html=True)
