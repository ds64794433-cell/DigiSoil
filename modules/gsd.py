import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.interpolate import make_interp_spline
import os

def interpolate_d(target, sieve, percent):
    # Ensure arrays are sorted by percent finer for consistent interpolation
    for i in range(len(percent) - 1):
        if (percent[i] >= target >= percent[i + 1]) or (percent[i] <= target <= percent[i + 1]):
            x1 = np.log10(sieve[i])
            x2 = np.log10(sieve[i + 1])
            y1 = percent[i]
            y2 = percent[i + 1]
            if y1 == y2: return 10**x1
            x = x1 + (target - y1) * (x2 - x1) / (y2 - y1)
            return 10 ** x
    return None

def run():
    st.title("Grain Size Distribution (Sieve Analysis)")
    
    # 1. Input: Total Sample Weight
    total_sample_weight = st.number_input("Total Sample Weight (g)", min_value=0.0, step=0.01, value=None)

    # Define Sieve Standards
    sieve_labels = ["4.75 ", "2.36 ", "1.18 ", "0.850 ", "0.600 ", "0.425 ", "0.300 ", "0.150 ", "0.075 ", "Pan"]
    sieve_sizes = [4.75, 2.36, 1.18, 0.850, 0.600, 0.425, 0.300, 0.150, 0.075, 0.001]

    # 2. Input: Sieve Weights
    st.subheader("Laboratory Data Input")
    if "gsd_input_data" not in st.session_state:
        st.session_state.gsd_input_data = pd.DataFrame({
            "Sieve Size (mm)": sieve_labels, 
            "Weight Retained (g)": [0.0]*10
        })

    edited_df = st.data_editor(st.session_state.gsd_input_data, num_rows="fixed")

    if st.button("Calculate GSD"):
        weights = edited_df["Weight Retained (g)"].values
        
        if total_sample_weight is None or total_sample_weight == 0:
            st.error("Please enter total sample weight.")
            return

        # Core Calculations
        percent_retained = (weights / total_sample_weight) * 100
        cumulative_percent_retained = np.cumsum(percent_retained)
        percent_finer = 100 - cumulative_percent_retained

        # 3. Store Results in Session State for Classification
        gravel_val = cumulative_percent_retained[0] # Retained on 4.75mm
        fines_val = percent_finer[8]                # Passing 0.075mm
        sand_val = 100 - gravel_val - fines_val
        
        st.session_state.update({
            "gravel_percent": gravel_val,
            "sand_percent": sand_val,
            "fines_result": fines_val
        })
        
        st.success(f"✅ Data Saved: Gravel={gravel_val:.1f}%, Sand={sand_val:.1f}%, Fines={fines_val:.1f}%")

        # 4. Display Comprehensive Results Table
        st.subheader("Analysis Results Table")
        result_df = pd.DataFrame({
            "Sieve Size": sieve_labels,
            "Weight Retained (g)": weights,
            "% Retained": percent_retained,
            "Cum. % Retained": cumulative_percent_retained,
            "% Finer": percent_finer
        })
        
        st.dataframe(result_df.style.format({
            "Weight Retained (g)": "{:.2f}",
            "% Retained": "{:.2f}%",
            "Cum. % Retained": "{:.2f}%",
            "% Finer": "{:.2f}%"
        }))

        # 5. Interpolation for D10, D30, D60 (Cu/Cc)
        sieve_for_interp = sieve_sizes[:-1]
        finer_for_interp = percent_finer[:-1]
        D10 = interpolate_d(10, sieve_for_interp, finer_for_interp)
        D30 = interpolate_d(30, sieve_for_interp, finer_for_interp)
        D60 = interpolate_d(60, sieve_for_interp, finer_for_interp)

        if D10 and D30 and D60:
            cu = D60 / D10
            cc = (D30**2) / (D10 * D60)
            st.session_state["cu_result"] = cu
            st.session_state["cc_result"] = cc
            st.info(f"**Coefficients:** Cu = {cu:.2f}, Cc = {cc:.2f}")
        else:
            st.warning("⚠️ Data points insufficient to calculate Cu and Cc (D10, D30, or D60 out of range).")
# 6. Plotting the Semi-Log GSD Curve
        st.subheader("Grain Size Distribution Curve")
        
        # --- FIX: Ensure x values are strictly increasing for the spline ---
        # Current x (sieve_sizes) is descending. We need ascending for the math.
        x = np.array(sieve_sizes[:-1]) # [4.75, 2.36, ... 0.075]
        y = np.array(percent_finer[:-1])
        
        # Sort both by x (particle size) to ensure ascending order
        sort_idx = np.argsort(x)
        x_sorted = x[sort_idx]
        y_sorted = y[sort_idx]
        
        x_log = np.log10(x_sorted)
        
        # Create spline using sorted, increasing data
        x_new_log = np.linspace(x_log.min(), x_log.max(), 300)
        spline = make_interp_spline(x_log, y_sorted, k=3)
        y_smooth = spline(x_new_log)

        # Plot
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.semilogx(10**x_new_log, y_smooth, color='navy', label='Smooth Curve', linewidth=2)
        ax.scatter(x, y, color='red', s=30, zorder=5) # Original points
        
        ax.set_xlabel("Particle Size (mm) - Log Scale")
        ax.set_ylabel("Percent Finer (%)")
        ax.set_title("Grain Size Distribution Curve")
        ax.invert_xaxis() # Keep larger particles on the left
        ax.set_ylim(0, 105)
        ax.grid(True, which='both', linestyle='--', alpha=0.7)
        ax.xaxis.set_major_formatter(ScalarFormatter())
        
        st.pyplot(fig)
        
        # Save image for the PDF report
        fig.savefig("gsd_curve.png")
        
        with open("gsd_curve.png", "rb") as f:
            st.download_button("Download GSD Curve", f, "gsd_curve.png")

    if st.button("Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
