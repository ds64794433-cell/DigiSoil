import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def interpolate_d(target, sieve, percent):
    sieve = np.array(sieve)
    percent = np.array(percent)
    idx = np.argsort(percent)[::-1]
    s_sorted, p_sorted = sieve[idx], percent[idx]

    for i in range(len(p_sorted) - 1):
        if p_sorted[i] >= target >= p_sorted[i+1]:
            val1 = max(s_sorted[i], 0.0001)
            val2 = max(s_sorted[i+1], 0.0001)
            x1, x2 = np.log10(val1), np.log10(val2)
            y1, y2 = p_sorted[i], p_sorted[i+1]
            if y1 == y2: 
                return 10**x1
            x = x1 + (target - y1) * (x2 - x1) / (y2 - y1)
            return 10**x
    return None

def run():
    st.title("🏗️ Grain Size Analysis (Sieve Analysis Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-4):1985")

    if "calculated" not in st.session_state:
        st.session_state.calculated = False

    total_sample_weight = st.number_input("Total Sample Weight (g)", min_value=0.1, value=1000.0)

    sieve_labels = ["4.75 mm", "2.36 mm", "1.18 mm", "0.600 mm", "0.425 mm", "0.212 mm", "0.150 mm", "0.075 mm", "Pan"]
    sieve_sizes = [4.75, 2.36, 1.18, 0.600, 0.425, 0.212, 0.150, 0.075, 0.001]

    if "gsd_input_data" not in st.session_state or len(st.session_state.gsd_input_data) != len(sieve_labels):
        st.session_state.gsd_input_data = pd.DataFrame({
            "Sieve Size": sieve_labels, 
            "Weight Retained (g)": [0.0] * len(sieve_labels)
        })

    edited_df = st.data_editor(st.session_state.gsd_input_data, use_container_width=True)

    if st.button("🚀 Calculate & Generate Curve"):
        weights = edited_df["Weight Retained (g)"].values
        sum_of_weights = np.sum(weights)
        
        if abs(sum_of_weights - total_sample_weight) > 0.1:
            st.error(f"❌ Data Entry Error! Sum ({sum_of_weights:.2f}g) doesn't match Total ({total_sample_weight:.2f}g).")
            st.session_state.calculated = False
        else:
            st.success("✅ Data Validated!")
            st.session_state.calculated = True

    # --- ALL CALCULATION LOGIC MUST BE INSIDE THIS IF BLOCK AND INDENTED ---
    if st.session_state.calculated:
        weights = edited_df["Weight Retained (g)"].values
        percent_retained = (weights / total_sample_weight) * 100
        cum_retained = np.cumsum(percent_retained)
        percent_finer = 100 - cum_retained
        
        x_points = np.array(sieve_sizes)
        y_points = np.array(percent_finer)

        # Correct Indexing for 0.075mm (Index 7)
        gravel = cum_retained[0]
        fines = percent_finer[7] 
        sand = 100 - gravel - fines

        D10 = interpolate_d(10, x_points, y_points)
        D30 = interpolate_d(30, x_points, y_points)
        D60 = interpolate_d(60, x_points, y_points)

        cu, cc = None, None
        if D10 and D60 and D10 > 0:
            cu = D60 / D10
            cc = (D30**2) / (D10 * D60) if D30 else None

        # Syncing with session state for full_classification.py
        st.session_state.update({
            "d10_val": D10, "d30_val": D30, "d60_val": D60,
            "cu_result": cu, "cc_result": cc,
            "gravel_percent": gravel, "fines_percent": fines, "sand_percent": sand
        })

        st.subheader("📌 Grain Size Parameters")
        def fmt(val, precision=3):
            return f"{val:.{precision}f}" if val is not None else "N/A"

        param_df = pd.DataFrame({
            "Parameter": ["D60 (mm)", "D30 (mm)", "D10 (mm)", "Cu (Uniformity)", "Cc (Curvature)"],
            "Value": [fmt(D60), fmt(D30), fmt(D10), fmt(cu, 2), fmt(cc, 2)]
        })
        st.table(param_df)

        st.subheader("📈 Particle Size Distribution Curve")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.semilogx(x_points, y_points, color='#1f77b4', marker='o', mfc='red', markersize=8, linewidth=2.5, label='Soil Sample')
            
        for d_val, label, color in zip([D60, D30, D10], ["D60", "D30", "D10"], ["orange", "green", "purple"]):
            if d_val:
                target_y = int(label[1:])
                ax.hlines(y=target_y, xmin=d_val, xmax=5.0, colors=color, linestyles='--', alpha=0.6)
                ax.vlines(x=d_val, ymin=0, ymax=target_y, colors=color, linestyles='--', alpha=0.6, label=f"{label}: {d_val:.3f} mm")

        ax.set_xlim(5.0, 0.001)
        ax.set_ylim(0, 105)
        ax.set_xlabel("Particle Size (mm) - Log Scale", fontweight='bold')
        ax.set_ylabel("Percent Passing (%)", fontweight='bold')
        ax.grid(True, which='both', linestyle=':', alpha=0.5)
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.legend(loc='upper left')
        plt.text(0.95, 0.05, 'DigiSoil | MITS Gwalior', transform=ax.transAxes, ha='right', alpha=0.3)
        st.pyplot(fig)
        fig.savefig("gsd_curve.png", dpi=300, bbox_inches='tight')

        col_down, _ = st.columns(2)
        with col_down:
            with open("gsd_curve.png", "rb") as file:
                st.download_button(label="📥 Download Graph", data=file, file_name="MITS_GSD.png", mime="image/png")

    # --- Back to Home Button (Outside the calculation check) ---
    st.divider()
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
