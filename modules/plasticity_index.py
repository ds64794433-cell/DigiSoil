import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def run():
    st.header("📈 Plasticity Index & IS Chart")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    # 1. Retrieve data from session state
    ll = st.session_state.get("liquid_limit_val", 0.0)
    pl = st.session_state.get("plastic_limit_val", 0.0)

    # Check if data actually exists before proceeding
    if ll == 0.0 or pl == 0.0:
        st.warning("⚠️ Data Missing: Please complete Liquid Limit and Plastic Limit tabs first.")
        return

    # --- DATA VALIDATION LOGIC ---
    if pl > ll:
        st.error(f"❌ **Data Entry Error:** Plastic Limit ({pl}%) is greater than Liquid Limit ({ll}%).")
        st.info("This is physically impossible. Please re-check your laboratory weights in the LL and PL sections.")
        return # Stops the rest of the code from running

    elif pl == ll:
        pi = 0.0
        st.warning("⚠️ **Soil is Non-Plastic (NP):** The Liquid Limit and Plastic Limit are equal.")
    else:
        pi = ll - pl

    # Save PI result for other parts of the app
    st.session_state.pi_result = pi

    # 2. Display Metrics Summary
    st.subheader("Atterberg Limits Summary")
    cols = st.columns(3)
    cols[0].metric("Liquid Limit (LL)", f"{ll:.2f}%")
    cols[1].metric("Plastic Limit (PL)", f"{pl:.2f}%")
    cols[2].metric("Plasticity Index (PI)", f"{pi:.2f}%")

    # 3. Plasticity Chart Visualization
    st.subheader("IS Plasticity Chart (Casagrande)")
    
    fig, ax = plt.subplots(figsize=(8, 6))

    # Formulas for standard lines
    ll_range = np.linspace(0, 100, 500)
    # A-Line: PI = 0.73 * (LL - 20)
    a_line = 0.73 * (ll_range - 20)
    a_line = np.maximum(0, a_line) # Ensure PI doesn't go negative on plot
    
    # U-Line (Upper Boundary): PI = 0.9 * (LL - 8)
    u_line = 0.9 * (ll_range - 8)
    u_line = np.maximum(0, u_line)

    # Plot lines
    ax.plot(ll_range, a_line, color='black', linewidth=2, label='A-Line (PI = 0.73(LL-20))', zorder=2)
    ax.plot(ll_range, u_line, color='red', linestyle='--', alpha=0.4, label='U-Line (Upper Limit)', zorder=1)
    
    # Plot the Soil Sample
    ax.scatter(ll, pi, color='blue', s=200, marker='X', edgecolors='white', zorder=10, label=f'Your Soil (LL:{ll}, PI:{pi})')

    # Chart Zoning (Vertical limits per IS Code)
    ax.axvline(35, color='gray', linestyle=':', alpha=0.5) # Low compressibility
    ax.axvline(50, color='gray', linestyle=':', alpha=0.5) # High compressibility
    
    # Formatting
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.set_xlabel("Liquid Limit (LL) %", fontweight='bold')
    ax.set_ylabel("Plasticity Index (PI) %", fontweight='bold')
    ax.set_title("Indian Standard Soil Classification Chart", fontweight='bold')
    
    # Annotate Zones
    ax.text(10, 5, 'NP / ML', fontsize=8, color='green')
    ax.text(25, 15, 'CL-ML', fontsize=8, rotation=35)
    ax.text(40, 30, 'CI', fontsize=10, fontweight='bold')
    ax.text(75, 45, 'CH', fontsize=10, fontweight='bold')
    ax.text(75, 10, 'MH / OH', fontsize=10)
    
    ax.grid(True, which='both', linestyle=':', alpha=0.4)
    ax.legend(loc='upper left')
    
    st.pyplot(fig)

    # 4. Result Explanation & Final Classification
    st.divider()
    a_line_val = 0.73 * (ll - 20)
    
    if pi == 0:
        st.success("✅ **Final Classification:** The soil is **Non-Plastic (NP)**.")
    elif pi > a_line_val:
        if ll < 35:
            st.success(f"✅ **Classification:** **CL** (Low Plasticity Clay). PI ({pi:.1f}) > A-Line ({a_line_val:.1f}).")
        elif 35 <= ll <= 50:
            st.success(f"✅ **Classification:** **CI** (Intermediate Plasticity Clay).")
        else:
            st.success(f"✅ **Classification:** **CH** (High Plasticity Clay).")
    elif pi < a_line_val:
        if ll < 35:
            st.info(f"ℹ️ **Classification:** **ML / OL** (Low Plasticity Silt/Organic).")
        elif 35 <= ll <= 50:
            st.info(f"ℹ️ **Classification:** **MI / OI** (Intermediate Plasticity Silt/Organic).")
        else:
            st.info(f"ℹ️ **Classification:** **MH / OH** (High Plasticity Silt/Organic).")
    else:
        st.warning("⚠️ **Classification:** Soil falls exactly on the A-Line boundary.")

    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
