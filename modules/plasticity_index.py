import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def run():
    st.header("📈 Plasticity Index & IS Chart")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    ## Inside run() in plasticity_index.py

    # 1. Retrieve data using the CORRECT keys
    ll = st.session_state.get("liquid_limit_val", 0.0)
    pl = st.session_state.get("plastic_limit_val", 0.0)

    # 2. Check if data actually exists
    if ll == 0.0 or pl == 0.0:
        st.warning("⚠️ Data Missing: Please complete Liquid Limit and Plastic Limit tabs first.")
        return

    # 3. If data is found, calculate PI
    pi = ll - pl
    st.session_state.pi_result = pi # Save PI for the final classification page

    # 2. Display Metrics
    st.subheader("Atterberg Summary")
    cols = st.columns(3)
    cols[0].metric("Liquid Limit (LL)", f"{ll:.2f}%")
    cols[1].metric("Plastic Limit (PL)", f"{pl:.2f}%")
    cols[2].metric("Plasticity Index (PI)", f"{pi:.2f}%")

    # 3. Plasticity Chart Visualization
    st.subheader("IS Plasticity Chart (Casagrande)")
    
    fig, ax = plt.subplots(figsize=(8, 6))

    # A-Line Formula: PI = 0.73 * (LL - 20)
    ll_range = np.linspace(20, 100, 100)
    a_line = 0.73 * (ll_range - 20)

    # Plot A-line
    ax.plot(ll_range, a_line, color='black', linewidth=2, label='A-Line (PI = 0.73(LL-20))')
    
    # Plot the Soil Sample
    ax.scatter(ll, pi, color='red', s=150, marker='X', zorder=5, label='Your Soil Sample')

    # Chart Zoning
    ax.axvline(35, color='gray', linestyle='--', alpha=0.5) # Low to Intermediate
    ax.axvline(50, color='gray', linestyle='--', alpha=0.5) # Intermediate to High
    
    # Formatting the Chart
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.set_xlabel("Liquid Limit (LL) %", fontweight='bold')
    ax.set_ylabel("Plasticity Index (PI) %", fontweight='bold')
    ax.set_title("Plasticity Chart for Soil Classification", fontweight='bold')
    
    # Zone Labels
    ax.text(25, 40, 'CL-ML', fontsize=9, color='blue')
    ax.text(40, 40, 'CI', fontsize=10, fontweight='bold')
    ax.text(70, 40, 'CH', fontsize=10, fontweight='bold')
    ax.text(45, 5, 'MI / OI', fontsize=10)
    
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)

    # 4. Result Explanation
    a_line_val = 0.73 * (ll - 20)
    st.divider()
    if pi > a_line_val and pi > 7:
        st.success(f"✅ **Classification:** Fines are **Clayey (C)**. PI ({pi:.1f}) is above the A-Line ({a_line_val:.1f}).")
    elif pi < a_line_val or pi < 4:
        st.info(f"ℹ️ **Classification:** Fines are **Silty (M)**. PI ({pi:.1f}) is below the A-Line ({a_line_val:.1f}).")
    else:
        st.warning("⚠️ **Classification:** Soil falls in the **CL-ML (Dual)** transition zone.")

    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()
