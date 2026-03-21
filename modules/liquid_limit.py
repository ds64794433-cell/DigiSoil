import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def run():
    st.header("💧 Liquid Limit Test (Casagrande Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    st.write("Enter laboratory data below. Ensure all 4 columns in a row are filled.")

    # 1. INITIALIZE TABLE
    if "ll_data" not in st.session_state:
        st.session_state.ll_data = pd.DataFrame({
            "No. of Blows": [None, None, None],
            "Weight of Container (g)": [None, None, None],
            "Weight of Wet Soil + Cont. (g)": [None, None, None],
            "Weight of Dry Soil + Cont. (g)": [None, None, None]
        })

    st.subheader("Laboratory Data Input")
    edited_df = st.data_editor(st.session_state.ll_data, num_rows="fixed", key="ll_editor")

    if st.button("🚀 Calculate Liquid Limit"):
        # 2. CLEANING DATA: Inside the button block
        df_clean = edited_df.dropna(how='any')
        df_clean = df_clean.apply(pd.to_numeric, errors='coerce').dropna()

        if len(df_clean) < 3:
            st.error("❌ Please enter 3 complete rows of lab data.")
            return

        # 3. EXTRACT SYNCHRONIZED ARRAYS
        blows = df_clean["No. of Blows"].values
        w_cont = df_clean["Weight of Container (g)"].values
        w_wet = df_clean["Weight of Wet Soil + Cont. (g)"].values
        w_dry = df_clean["Weight of Dry Soil + Cont. (g)"].values

        # 4. CALCULATE WATER CONTENT
        water_contents = []
        for i in range(len(df_clean)):
            w_water = w_wet[i] - w_dry[i]
            w_soil = w_dry[i] - w_cont[i]
            
            if w_soil <= 0:
                st.error(f"❌ Trial {i+1}: Dry soil weight must be positive.")
                return
            
            wc = (w_water / w_soil) * 100
            water_contents.append(wc)

        water_contents = np.array(water_contents)

        # 5. MATH: LOG-LINEAR REGRESSION
        try:
            log_n = np.log10(blows.astype(float))
            m, c = np.polyfit(log_n, water_contents, 1)
            ll_25 = m * np.log10(25) + c

            # SAVE TO SESSION STATE
            st.session_state.liquid_limit_val = round(ll_25, 2)
            st.success(f"✅ Liquid Limit (LL) = **{ll_25:.2f}%**")

            # 6. Professional Plotting
            fig, ax = plt.subplots(figsize=(8, 6))
            min_blow, max_blow = min(blows), max(blows)
            plot_min, plot_max = min_blow * 0.8, max_blow * 1.2
            ax.set_xlim(plot_min, plot_max)
            
            # Flow Curve
            x_fit = np.logspace(np.log10(min_blow), np.log10(max_blow), 100)
            y_fit = m * np.log10(x_fit) + c
            ax.semilogx(x_fit, y_fit, color='#1f77b4', label='Flow Curve', linewidth=2, zorder=2)
            ax.scatter(blows, water_contents, color='red', s=80, zorder=5, label='Trials')

            # Intersection Lines
            if plot_min <= 25 <= plot_max:
                ax.vlines(x=25, ymin=min(water_contents)-2, ymax=ll_25, 
                          color='green', linestyle='--', alpha=0.8, linewidth=1.5, zorder=3)
                ax.hlines(y=ll_25, xmin=plot_min, xmax=25, 
                          color='green', linestyle='--', alpha=0.8, linewidth=1.5, zorder=3)
                ax.annotate(f'LL={ll_25:.1f}%', xy=(25, ll_25), xytext=(25*1.1, ll_25 + 0.5),
                            color='green', fontweight='bold')

            ax.set_xlabel("Number of Blows (N) - Log Scale", fontweight='bold')
            ax.set_ylabel("Water Content (%)", fontweight='bold')
            ax.xaxis.set_major_formatter(ScalarFormatter())
            ax.grid(True, which='both', alpha=0.3)
            ax.legend()
            
            st.pyplot(fig)

            # Save image for report
            fig.savefig("ll_curve.png", dpi=300, bbox_inches='tight')
            
            with open("ll_curve.png", "rb") as file:
                st.download_button(
                    label="📥 Download Flow Curve (PNG)",
                    data=file,
                    file_name=f"DigiSoil_LL_Curve_{ll_25:.1f}.png",
                    mime="image/png",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"📈 Error generating graph: {e}")

    # --- HOME BUTTON (Aligned with the calculate button) ---
    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
