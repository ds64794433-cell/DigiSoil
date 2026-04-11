import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.interpolate import pchip_interpolate
import io

def interpolate_d(target, sieve, percent):
    sieve = np.array(sieve)
    percent = np.array(percent)
    idx = np.argsort(percent)[::-1]
    s_sorted, p_sorted = sieve[idx], percent[idx]

    if target < min(p_sorted):
        return None

    for i in range(len(p_sorted) - 1):
        if p_sorted[i] >= target >= p_sorted[i+1]:
            val1 = max(s_sorted[i], 0.0001)
            val2 = max(s_sorted[i+1], 0.0001)
            x1, x2 = np.log10(val1), np.log10(val2)
            y1, y2 = p_sorted[i], p_sorted[i+1]
            if y1 == y2: return 10**x1
            x = x1 + (target - y1) * (x2 - x1) / (y2 - y1)
            return 10**x
    return None

def run():
    st.header("📊 Grain Size Distribution (Sieve Analysis)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-4):1985")

    # 1. INITIALIZE MASTER STORAGE
    if "gsd_master_v12" not in st.session_state:
        st.session_state.gsd_master_v12 = pd.DataFrame({
            "Sieve Size (mm)": [4.75, 2.36, 1.18, 0.600, 0.425, 0.212, 0.150, 0.075, 0.0],
            "Weight Retained (g)": [0.0] * 9
        })
    
    total_weight = st.number_input("Total Sample Weight (g)", min_value=0.1, value=1000.0, step=0.1)
    
    # 2. THE DATA EDITOR
    edited_output = st.data_editor(
        st.session_state.gsd_master_v12, 
        use_container_width=True,
        key="gsd_editor_v12"
    )

    if st.button("🚀 Calculate & Generate Report", use_container_width=True):
        # --- PRE-CALCULATION CHECK ---
        raw_edits = st.session_state.gsd_editor_v12
        df = st.session_state.gsd_master_v12.copy()
        for row_idx, changes in raw_edits["edited_rows"].items():
            for col_name, new_val in changes.items():
                df.at[int(row_idx), col_name] = new_val
        
        # Clean data to numeric
        df["Weight Retained (g)"] = pd.to_numeric(df["Weight Retained (g)"], errors='coerce').fillna(0.0).astype(float)
        st.session_state.gsd_master_v12 = df

        current_sum = float(df["Weight Retained (g)"].sum())
        # Tolerance of 0.1g for rounding errors
        if abs(current_sum - total_weight) > 0.1:
            # KILL OLD RESULTS
            if "gsd_final" in st.session_state:
                del st.session_state.gsd_final
            
            # SHOW WARNING
            st.error("❌ **Calculation Stopped!**")
            st.warning(f"Check your input data once. Sum of weights ({current_sum:.2f}g) is not equal to Total Sample Weight ({total_weight}g).")
            st.stop() # STOP EVERYTHING HERE

        # --- CALCULATIONS (Only runs if check passes) ---
        w_retained = df["Weight Retained (g)"].values
        p_retained = (w_retained / total_weight) * 100
        cum_p_retained = np.cumsum(p_retained)
        p_finer = 100 - cum_p_retained
        
        analysis_df = df.copy()
        analysis_df["% Retained"] = p_retained
        analysis_df["Cum. % Retained"] = cum_p_retained
        analysis_df["% Finer (Passing)"] = p_finer

        x_pts = df["Sieve Size (mm)"].values
        y_pts = p_finer

        d10 = interpolate_d(10, x_pts, y_pts)
        d30 = interpolate_d(30, x_pts, y_pts)
        d60 = interpolate_d(60, x_pts, y_pts)

        # Calculation with safety checks
        cu = d60 / d10 if (d10 and d60 and d10 > 0.001) else np.nan
        cc = (d30**2) / (d10 * d60) if (d10 and d30 and d60 and (d10*d60) > 0) else np.nan

        st.session_state.gsd_final = {
            "d10": d10, "d30": d30, "d60": d60, "cu": cu, "cc": cc,
            "table": analysis_df, "x": x_pts, "y": y_pts,
            "gravel": cum_p_retained[0], "fines": p_finer[7], 
            "sand": 100 - cum_p_retained[0] - p_finer[7]
        }
        st.success("✅ Weights Verified. Report Generated.")
        st.rerun()

    # --- 3. PERSISTENT RESULTS DISPLAY ---
    if "gsd_final" in st.session_state:
        res = st.session_state.gsd_final
        
        st.divider()
        st.subheader("📋 Sieve Analysis Calculation Table")
        st.table(res["table"].style.format(precision=2))

        st.subheader("📈 Particle Size Distribution Curve")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sort_idx = np.argsort(res['x'])
        x_s, y_s = res['x'][sort_idx], res['y'][sort_idx]

# Remove zero or invalid values
        mask = x_s > 0
        x_s, y_s = x_s[mask], y_s[mask]

# 🔥 DEFINE THESE (THIS WAS MISSING)
        x_smooth = np.logspace(np.log10(x_s.min()), np.log10(x_s.max()), 500)
        y_smooth = pchip_interpolate(x_s, y_s, x_smooth)

# Now plot
        ax.semilogx(x_smooth, y_smooth, color='#1E3A8A', linewidth=2.5, label='Gradation Curve', zorder=2)
        ax.scatter(res['x'], res['y'], color='#FF4B2B', s=80, edgecolors='white', zorder=5)

        # Draw D10, D30, D60 Lines
        line_data = [ (res['d60'], 60, '#FFA500', 'D60'), (res['d30'], 30, '#228B22', 'D30'), (res['d10'], 10, '#800080', 'D10') ]
        for val, percent, color, label in line_data:
            if val:
                ax.hlines(y=percent, xmin=val, xmax=10.0, colors=color, linestyles='--', alpha=0.7)
                ax.vlines(x=val, ymin=0, ymax=percent, colors=color, linestyles='--', alpha=0.7)
                ax.text(val, 2, f' {label}', color=color, fontweight='bold', fontsize=9)

        ax.set_xlim(10.0, 0.001)
        ax.set_ylim(0, 105)
        ax.set_xlabel("Particle Size (mm) [Log Scale]", fontweight='bold')
        ax.set_ylabel("Percentage Passing (%)", fontweight='bold')
        ax.grid(True, which='both', linestyle=':', alpha=0.6)
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.legend(loc='upper left')
        st.pyplot(fig)

        # Download Button
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        st.download_button("📥 Download Curve", buf.getvalue(), "MITS_GSD_Report.png", "image/png", use_container_width=True)

        # Parameters Table - Professional Formatting
        
        # 1. Prepare display values with safety checks
        d60_disp = f"{res['d60']:.3f} mm" if res['d60'] else "-"
        d30_disp = f"{res['d30']:.3f} mm" if res['d30'] else "-"
        
        # D10 is the most common to be missing in fine-grained soils
        d10_disp = f"{res['d10']:.3f} mm" if res['d10'] else "Use Hydrometer"

        # Check for NaN or 0 for Cu and Cc
        cu_val = res['cu']
        cc_val = res['cc']
        
        cu_disp = f"{cu_val:.2f}" if (not np.isnan(cu_val) and cu_val > 0) else "-"
        cc_disp = f"{cc_val:.2f}" if (not np.isnan(cc_val) and cc_val > 0) else "-"

        # 2. Render the table
        st.table(pd.DataFrame({
            "Property": ["D60", "D30", "D10", "Uniformity (Cu)", "Curvature (Cc)"],
            "Value": [d60_disp, d30_disp, d10_disp, cu_disp, cc_disp]
        }))

    st.divider()
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.nav_choice = "Home"
        st.rerun()
