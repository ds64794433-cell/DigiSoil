import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def run():
    st.header("💧 Liquid Limit Test (Casagrande Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    # 1. INITIALIZE TABLE
    if "ll_data_input" not in st.session_state:
        st.session_state.ll_data_input = pd.DataFrame({
            "No. of Blows": [28, 22, 18],
            "Wt. Container (g)": [15.0, 15.2, 14.8],
            "Wt. Wet Soil + Cont. (g)": [35.5, 38.2, 40.1],
            "Wt. Dry Soil + Cont. (g)": [30.2, 31.5, 32.4]
        })

    st.subheader("Laboratory Data Input")
    edited_df = st.data_editor(st.session_state.ll_data_input, num_rows="fixed", key="ll_editor")

    if st.button("🚀 Calculate Liquid Limit"):
        df_clean = edited_df.apply(pd.to_numeric, errors='coerce').dropna()
        
        if len(df_clean) < 3:
            st.error("❌ Please enter at least 3 complete rows of data.")
            return

        blows = df_clean.iloc[:, 0].values
        w_cont = df_clean.iloc[:, 1].values
        w_wet = df_clean.iloc[:, 2].values
        w_dry = df_clean.iloc[:, 3].values

        water_contents = []
        for i in range(len(df_clean)):
            # CHECK 1: Physical impossibility (Dry > Wet)
            if w_dry[i] >= w_wet[i]:
                st.error(f"❌ Row {i+1}: Dry weight cannot be ≥ Wet weight.")
                return 

            # CHECK 2: Container weight logic
            if w_cont[i] >= w_dry[i]:
                st.error(f"❌ Row {i+1}: Container weight cannot be ≥ Dry soil weight.")
                return

            w_water = w_wet[i] - w_dry[i]
            w_soil = w_dry[i] - w_cont[i]
            water_contents.append((w_water / w_soil) * 100)

        # CHECK 3: Trend Validation
        # In Casagrande, higher blows (N) MUST mean lower water content (w).
        # We check if the correlation is negative as it should be.
        correlation = np.corrcoef(blows, water_contents)[0, 1]
        if correlation > 0:
            st.warning("⚠️ Warning: Data shows water content increasing with blow count. This is physically incorrect for a standard LL test.")

        # 3. MATH: REGRESSION
        try:
            log_n = np.log10(blows.astype(float))
            m, c = np.polyfit(log_n, water_contents, 1)
            ll_25 = m * np.log10(25) + c

            # CHECK 4: Result Validation
            if ll_25 <= 0:
                st.error(f"❌ Calculated LL is {ll_25:.2f}%. Check if your weights or blow counts are swapped.")
                return

            st.session_state.ll_plot_data = {
                'blows': blows, 'wc': water_contents, 
                'm': m, 'c': c, 'll': ll_25
            }
            st.session_state.liquid_limit_val = round(ll_25, 2)
            st.rerun() 

        except Exception as e:
            st.error(f"📈 Regression Error: {e}")

    # --- 4. PERSISTENT DISPLAY ---
    if "liquid_limit_val" in st.session_state:
        data = st.session_state.ll_plot_data
        ll_val = st.session_state.liquid_limit_val
        
        st.write("---")
        st.success(f"✅ Liquid Limit (LL) = **{ll_val}%**")
        
        # Plotting logic...
        fig, ax = plt.subplots(figsize=(8, 5))
        x_fit = np.linspace(10, 50, 100)
        y_fit = data['m'] * np.log10(x_fit) + data['c']
        
        ax.semilogx(x_fit, y_fit, color='#FF4B2B', label='Flow Curve')
        ax.scatter(data['blows'], data['wc'], color='#1E3A8A', label='Trials')
        ax.axvline(25, color='green', linestyle='--')
        ax.axhline(ll_val, color='green', linestyle='--')
        
        ax.set_xlabel("Number of Blows (N)")
        ax.set_ylabel("Water Content (%)")
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.grid(True, which='both', linestyle=':')
        st.pyplot(fig)

    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()
