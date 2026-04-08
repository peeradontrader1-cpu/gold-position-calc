import streamlit as st
import feedparser
import pandas as pd

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Gold Terminal Pro + News", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Playfair Display', serif; font-size: 42px; font-weight: 700; text-align: center; }
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] { background-color: #0A0A0A !important; color: #FFFFFF !important; border: 1px solid #222222 !important; border-radius: 4px !important; }
    div[data-testid="stMetric"] { background-color: #050505; border: 1px solid #1A1A1A; padding: 20px; border-radius: 4px; }
    .news-table { font-size: 12px; color: #BBB; border-collapse: collapse; width: 100%; }
    .news-table th { text-align: left; color: #666; border-bottom: 1px solid #222; padding: 8px; }
    .news-table td { padding: 8px; border-bottom: 1px dotted #111; }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNCTION: FETCH ECONOMIC NEWS ---
def get_economic_news():
    # ดึงข้อมูลจาก RSS Feed ของ Forex Factory (เป็นแหล่งที่เสถียรที่สุดสำหรับการดึงข้อมูลฟรี)
    url = "https://www.forexfactory.com/ff_calendar_thisweek.xml"
    try:
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries:
            # กรองเฉพาะข่าว USD เพราะมีผลกับราคาทองคำโดยตรง
            if entry.get('currency') == 'USD':
                news_items.append({
                    "Time": entry.get('updated', 'N/A'),
                    "Event": entry.get('title', 'N/A'),
                    "Impact": entry.get('impact', 'N/A')
                })
        return pd.DataFrame(news_items).head(10) # เอา 10 ข่าวล่าสุด
    except:
        return pd.DataFrame(columns=["Time", "Event", "Impact"])

# --- 3. HEADER & CALCULATOR (คงเดิมตามคำสั่งคุณ) ---
st.markdown('<p class="main-title">GOLD TERMINAL</p>', unsafe_allow_html=True)
if st.button("RESET TERMINAL"): st.rerun()
st.markdown("<hr style='border-top: 1px solid #111;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### ACCOUNT STATUS")
    balance = st.number_input("Current Equity ($)", value=50519.0)
    final_risk_usd = st.number_input("Risk per Trade ($)", value=100.0)

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
    contracts = final_risk_usd / (dist_sl * multiplier)
    st.markdown("<hr style='border-top: 1px solid #111;'>", unsafe_allow_html=True)
    res1, res2, res3 = st.columns(3)
    res1.metric("DISTANCE", f"{dist_sl:.2f}")
    res2.metric("RR RATIO", f"1:{dist_tp/dist_sl:.2f}")
    res3.metric("SIZE (CONS)", f"{contracts:.2f}")

    if contracts > 5: st.error(f"⚠️ EXCEEDS LIMIT: {contracts:.2f}")
    elif contracts < 1.0: st.error(f"⚠️ INSUFFICIENT: {contracts:.2f} (MIN 1.00)")
    else: st.success(f"PROCEED: {contracts:.2f} Cons.")

# --- 5. ECONOMIC CALENDAR SECTION (เพิ่มใหม่) ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### 📅 Market Radar: USD Events")
with st.spinner("Fetching latest news..."):
    df_news = get_economic_news()
    if not df_news.empty:
        # แสดงผลเป็นตารางสไตล์เรียบหรู
        st.table(df_news)
    else:
        st.info("No major USD news found at this moment.")

st.markdown("<p style='font-size:10px; color:#444;'>Data source: Forex Factory RSS Feed</p>", unsafe_allow_html=True)
