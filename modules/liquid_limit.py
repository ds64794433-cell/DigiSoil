import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import io

def run():
    st.header("💧 Liquid Limit Test (Casagrande Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    # 1. INITIALIZE MASTER STORAGE (The "Hard Drive" of your app)
    # Using v4 to ensure a fresh start from any previous errors
    if "ll_master_v4" not in st.session_state:
        st.session_state.ll_master_v4 = pd.DataFrame({
            "No. of Blows": [None, None, None],
            "Wt. Container (g)": [None, None, None],
            "Wt. Wet Soil + Cont. (g)": [None, None, None],
            "Wt. Dry Soil + Cont. (g)": [None, None, None]
        })

    st.subheader("Laboratory Data Input")
    
    # 2. THE DATA EDITOR (The "Input Screen")
    # We use a unique key 'll_editor_v4' to keep the widget memory stable
    st.data_editor(
        st.session_state.ll_master_v4, 
        num_rows="fixed", 
        use_container_width=True,
        key="ll_editor_v4" 
    )

    # 3. THE CALCULATION LOGIC
    if st.button("🚀 Calculate Liquid Limit"):
        # Access the widget's internal buffer
        raw_edits = st.session_state.ll_editor_v4
        df = st.session_state.ll_master_v4.copy()
        
        # Merge any changes made in the UI back into our Master DataFrame
        for row_idx, changes in raw_edits["edited_rows"].items():
            for col_name, new_val in changes.items():
                df.at[int(row_idx), col_name] = new_val
        
        # Save the merged data so it doesn't disappear on the next 'blink'
        st.session_state.ll_master_v4 = df
        
        # Clean data for math (remove any empty rows)
        df_clean = df.apply(pd.to_numeric, errors='coerce').dropna()
        
        if len(df_clean) < 3:
            st.error("❌ Please fill all 3 rows with valid numbers.")
        else:
            try:
                blows = df_clean.iloc[:, 0].values
                    
                # --- Blow Range Validation (STRICT: Stop if invalid) ---
                out_of_range = [int(b) for b in blows if b < 10 or b > 40]

                if len(out_of_range) > 0:
                    st.error(
                        f"❌ Invalid Data: Blow count(s) {out_of_range} are outside the standard range (10–40). "
                        "Liquid Limit calculation stopped. Please correct your lab data."
                    )
                return
                
                w_cont = df_clean.iloc[:, 1].values
                w_wet = df_clean.iloc[:, 2].values
                w_dry = df_clean.iloc[:, 3].values

                water_contents = []
                for i in range(len(df_clean)):
                    # Basic Weight Logic Check
                    if w_dry[i] >= w_wet[i] or w_cont[i] >= w_dry[i]:
                        st.error(f"❌ Row {i+1}: Weight error. (Dry cannot be > Wet, Cont cannot be > Dry)")
                        return
                    
                    w_water = w_wet[i] - w_dry[i]
                    w_soil = w_dry[i] - w_cont[i]
                    water_contents.append((w_water / w_soil) * 100)

                # Linear Regression on Log Scale
                log_n = np.log10(blows.astype(float))
                m, c = np.polyfit(log_n, water_contents, 1)
                
                # Calculate LL at 25 blows
                ll_25 = m * np.log10(25) + c
                
                # --- CRITICAL REQUIREMENT: CHECK FOR NEGATIVE LL ---
                if ll_25 <= 0:
                    st.error(f"❌ **Physical Error:** The calculated Liquid Limit is {ll_25:.2f}%. Soil moisture cannot be negative. Please check your laboratory weights.")
                    return

                # Check for Trend Error (Higher blows must mean lower water content)
                if m >= 0:
                    st.error("❌ **Data Trend Error:** Your data shows water content increasing with more blows. This is physically incorrect for a Casagrande test.")
                    return

                # SAVE EVERYTHING TO SESSION STATE
                st.session_state.liquid_limit_val = round(ll_25, 2)
                st.session_state.ll_plot_data = {
                    'blows': blows, 'wc': water_contents, 'm': m, 'c': c, 'll': ll_25
                }
                
                st.success(f"✅ Calculation Successful!")
                st.rerun() # Refresh to display results below

            except Exception as e:
                st.error(f"❌ Math/Regression Error: {str(e)}")

    # --- 4. PERSISTENT RESULTS & PLOTTING ---
    # This section stays on screen as long as 'liquid_limit_val' is in memory
    if "liquid_limit_val" in st.session_state:
        data = st.session_state.ll_plot_data
        ll_val = st.session_state.liquid_limit_val
        
        st.write("---")
        st.success(f"📊 **Result: Liquid Limit (LL) = {ll_val}%**")
        
        # Generate the Flow Curve
        fig, ax = plt.subplots(figsize=(8, 5))
        x_fit = np.logspace(np.log10(10), np.log10(60), 100)
        y_fit = data['m'] * np.log10(x_fit) + data['c']
        
        # Plotting styling
        ax.axvline(25, color='green', linestyle='--', alpha=0.3, label='25 Blows')
        ax.axhline(ll_val, color='green', linestyle='--', alpha=0.3)
        ax.semilogx(x_fit, y_fit, color='#FF4B2B', linewidth=2, label='Flow Curve')
        ax.scatter(data['blows'], data['wc'], color='#1E3A8A', s=80, label='Test Trials', zorder=5)
        ax.scatter([25], [ll_val], color='green', s=120, edgecolors='white', zorder=6)
        
        ax.set_xlabel("Number of Blows (N) - Log Scale")
        ax.set_ylabel("Water Content (%)")
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.grid(True, which='both', linestyle=':', alpha=0.5)
        ax.legend()
        
        st.pyplot(fig)

        # DOWNLOAD BUTTON
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        st.download_button(
            label="💾 Download LL Flow Curve Image",
            data=buf.getvalue(),
            file_name="liquid_limit_flow_curve.png",
            mime="image/png"
        )

    # --- 5. NAVIGATION (ALWAYS VISIBLE AT BOTTOM) ---
    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()
