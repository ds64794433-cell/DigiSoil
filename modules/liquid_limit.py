import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter

def run():
    st.header("Liquid Limit (Casagrande Method)")

    st.write("Enter laboratory data below. The app will validate the trend before calculating.")

    # 1. Initialize 3x4 Table (Empty by default)
    df_input = pd.DataFrame({
        "No. of Blows": [None, None, None],
        "Weight of Container (g)": [0.0, 0.0, 0.0],
        "Weight of Wet Soil + Cont. (g)": [0.0, 0.0, 0.0],
        "Weight of Dry Soil + Cont. (g)": [0.0, 0.0, 0.0]
    })

    st.subheader("Laboratory Data Input")
    # Streamlit native behavior: Enter moves to next cell
    edited_df = st.data_editor(df_input, num_rows="fixed", key="ll_editor")

    if st.button("Calculate Liquid Limit"):
        # Convert to numeric and extract
        df_num = edited_df.apply(pd.to_numeric, errors='coerce')
        blows = df_num["No. of Blows"].values
        w_cont = df_num["Weight of Container (g)"].values
        w_wet = df_num["Weight of Wet Soil + Cont. (g)"].values
        w_dry = df_num["Weight of Dry Soil + Cont. (g)"].values

        # Validation: Ensure blow counts are present
        if np.isnan(blows).any():
            st.error("❌ Error: Please fill in all 'No. of Blows' cells.")
            return

        # 2. Calculate Water Content
        water_contents = []
        for i in range(3):
            w_water = w_wet[i] - w_dry[i]
            w_soil = w_dry[i] - w_cont[i]
            
            if w_soil <= 0:
                st.error(f"❌ Error in Trial {i+1}: Dry soil weight must be positive.")
                return
            
            wc = (w_water / w_soil) * 100
            water_contents.append(wc)

        water_contents = np.array(water_contents)

        # 3. Strict Validation: Trend Check
        # Sort by blows to check physical trend (Water content must decrease as blows increase)
        sorted_idx = np.argsort(blows)
        sorted_wc = water_contents[sorted_idx]
        
        if any(sorted_wc[i] < sorted_wc[i+1] for i in range(len(sorted_wc)-1)):
            st.error("❌ **Invalid Lab Data:** Water content must decrease as the number of blows increases. Calculation stopped.")
            return

        # 4. Calculation: Log-Linear Regression
        # Formula: w = m * log10(N) + c
        log_n = np.log10(blows.astype(float))
        m, c = np.polyfit(log_n, water_contents, 1)
        ll_25 = m * np.log10(25) + c

        if ll_25 <= 0:
            st.error(f"❌ **Error:** Calculated Liquid Limit ({ll_25:.2f}%) is non-physical.")
            return

        st.success(f"✅ Liquid Limit (LL) at 25 blows = **{ll_25:.2f}%**")
        st.session_state["ll_result"] = ll_25

        # 5. Professional Plotting
        fig, ax = plt.subplots(figsize=(8, 6))

        # Dynamically set X limits to the data range with a small buffer
        min_blow = min(blows)
        max_blow = max(blows)
        plot_min = min_blow * 0.8  # 20% margin
        plot_max = max_blow * 1.2  # 20% margin
        ax.set_xlim(plot_min, plot_max)
        
        # Plot best fit line restricted EXACTLY to the range of your data points
        x_fit = np.logspace(np.log10(min_blow), np.log10(max_blow), 100)
        y_fit = m * np.log10(x_fit) + c
        ax.semilogx(x_fit, y_fit, color='blue', label='Flow Curve', linewidth=2)
        
        # Plot data points
        ax.scatter(blows, water_contents, color='red', s=80, zorder=5, label='Trials')

        # Add Vertical and Horizontal Grid Lines
        ax.grid(True, which='major', color='gray', linestyle='-', alpha=0.6)
        ax.grid(True, which='minor', color='gray', linestyle=':', alpha=0.3)
        ax.xaxis.set_minor_locator(plt.LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=10))
        
        # Draw green guidelines at N=25
        if plot_min <= 25 <= plot_max:
            # Vertical line: Draw from the bottom X-axis up to the flow curve intersection point
            ax.vlines(x=25, ymin=min(water_contents) - 5, ymax=ll_25, 
                      color='green', linestyle='--', alpha=0.7, linewidth=1.5)
            
            # Horizontal line: Draw from the left Y-axis (min limit) to the X=25 mark
            ax.hlines(y=ll_25, xmin=min_blow * 0.8, xmax=25, 
                      color='green', linestyle='--', alpha=0.7, linewidth=1.5)
            
            # Add a clean label at the intersection
            ax.annotate(f'LL={ll_25:.1f}%', xy=(25, ll_25), xytext=(25, ll_25 + 0.5),
                        ha='center', color='green', fontweight='bold', fontsize=9)
        ax.set_xlabel("Number of Blows (N) - Log Scale")
        ax.set_ylabel("Water Content (%)")
        ax.set_title("Casagrande Flow Curve")
        
        # Force integer-like labels on X-axis
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.legend()
        st.pyplot(fig)

        # Download Button
        fig.savefig("ll_curve.png")
        with open("ll_curve.png", "rb") as file:
            st.download_button(
                label="Download Flow Curve",
                data=file,
                file_name="ll_curve.png",
                mime="image/png"
            )

    # 6. Navigation Button
    def reset_to_home():
        st.session_state.nav_choice = "Home"

    st.button("Back to Home", on_click=reset_to_home)

if __name__ == "__main__":
    run()
