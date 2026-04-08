# --- LOGIC การคำนวณที่ถูกต้อง ---
points_sl = abs(entry_p - sl_p)
points_tp = abs(entry_p - tp_p)

# กำหนด Multiplier ให้เป๊ะตามกฎ CME/Topstep
# GC (Standard) = $100 ต่อ 1 Point
# MGC (Micro) = $10 ต่อ 1 Point
if "MGC" in symbol:
    multiplier = 10
else:
    multiplier = 100

if points_sl > 0:
    # 1. หาว่าถ้าเทรด 1 คอนแทรค จะเสียเงินกี่เหรียญ
    risk_per_one_contract = points_sl * multiplier
    
    # 2. เอาเงินที่ยอมเสียได้ ตั้งหารด้วย ความเสี่ยงต่อ 1 คอนแทรค
    # สูตร: $100 (Risk) / ($5 * $10) = 2.00 Contracts
    contracts = final_risk_usd / risk_per_one_contract
    
    # คำนวณ RR Ratio
    rr_ratio = points_tp / points_sl if points_sl > 0 else 0

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- การแสดงผล (OUTPUT) ---
    st.subheader("EXECUTION DATA")
    res1, res2, res3 = st.columns(3)
    res1.metric("SL POINTS", f"{points_sl:.2f}")
    res2.metric("RR RATIO", f"1:{rr_ratio:.2f}")
    res3.metric("SIZE (CONS)", f"{contracts:.2f}") # ตรงนี้จะได้ 2.00 แล้วครับ
