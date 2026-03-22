import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def run():
    st.header("💧 Liquid Limit Test (Casagrande Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    st.write("Enter laboratory data below. Ensure all columns in at least 3 rows are filled.")

    # 1. INITIALIZE TABLE (Persistent in session state)
    if "ll_data_input" not in st.session_state:
        st.session_state.ll_data_input = pd.DataFrame({
            "No. of Blows": [28, 22, 18],
            "Wt. Container (g)": [0.0, 0.0, 0.0],
            "Wt. Wet Soil + Cont. (g)": [0.0, 0.0, 0.0],
            "Wt. Dry Soil + Cont. (g)": [0.0, 0.0, 0.0]
        })

    st.subheader("Laboratory Data Input")
    edited_df = st.data_editor(st.session_state.ll_data_input, num_rows="fixed", key="ll_editor")

    if st.button("🚀 Calculate Liquid Limit"):
        # Save input to state
        st.session_state.ll_data_input = edited_df
        
        # 2. CLEAN AND VALIDATE
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
            # --- PHYSICAL SANITY CHECKS ---
            if w_dry[i] > w_wet[i]:
                st.error(f"❌ Trial {i+1}: Dry weight ({w_dry[i]}g) cannot be more than Wet weight ({w_wet[i]}g). Check for entry errors!")
                return
            if w_cont[i] >= w_dry[i]:
                st.error(f"❌ Trial {i+1}: Container weight is higher than Dry Soil weight. Check your entries!")
                return

            w_water = w_wet[i] - w_dry[i]
            w_soil = w_dry[i] - w_cont[i]
            water_contents.append((w_water / w_soil) * 100)

        # 3. MATH: REGRESSION
        try:
            log_n = np.log10(blows.astype(float))
            m, c = np.polyfit(log_n, water_contents, 1)
            ll_25 = m * np.log10(25) + c

            # SAVE RESULTS (Sidebar status turns green ✅)
            st.session_state.liquid_limit_val = round(ll_25, 2)
            st.session_state.ll_plot_data = {
                'blows': blows, 
                'wc': water_contents, 
                'm': m, 
                'c': c, 
                'll': ll_25
            }
            st.rerun() 
        except Exception as e:
            st.error(f"📈 Regression Error: {e}")

    # --- 4. PERSISTENT DISPLAY (Outside Button) ---
    if "liquid_limit_val" in st.session_state:
        data = st.session_state.ll_plot_data
        ll_val = data['ll']
        
        st.write("---")
        st.success(f"✅ Liquid Limit (LL) = **{ll_val:.2f}%**")
        
        # Plotting
        fig, ax = plt.subplots(figsize=(8, 5))
        x_fit = np.logspace(np.log10(min(data['blows'])), np.log10(max(data['blows'])), 100)
        y_fit = data['m'] * np.log10(x_fit) + data['c']
        
        ax.semilogx(x_fit, y_fit, color='#FF4B2B', label='Flow Curve', linewidth=2)
        ax.scatter(data['blows'], data['wc'], color='#1E3A8A', s=100, label='Trials', zorder=5)
        
        # Intercepts
        ax.axvline(25, color='green', linestyle='--', alpha=0.5)
        ax.axhline(ll_val, color='green', linestyle='--', alpha=0.5)
        ax.set_xlabel("Number of Blows (N) - Log Scale")
        ax.set_ylabel("Water Content (%)")
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.legend()
        st.pyplot(fig)

    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
