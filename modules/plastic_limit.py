import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("Plastic Limit (PL) Determination")
    
    st.write("Enter the weights for 2 trials. The app will calculate the PL automatically.")

    # 2 rows, columns for weights only (No trial column)
    df_input = pd.DataFrame({
        "Container Wt (g)": [0.0, 0.0],
        "Wet Soil + Cont. (g)": [0.0, 0.0],
        "Dry Soil + Cont. (g)": [0.0, 0.0]
    }, index=["Trial 1", "Trial 2"]) # Setting row labels instead of a column

    st.subheader("Laboratory Data")
    edited_df = st.data_editor(df_input, num_rows="fixed", key="pl_editor")

    if st.button("Calculate Plastic Limit"):
        df_num = edited_df.apply(pd.to_numeric, errors='coerce')
        w_cont = df_num["Container Wt (g)"].values
        w_wet = df_num["Wet Soil + Cont. (g)"].values
        w_dry = df_num["Dry Soil + Cont. (g)"].values
        
        water_contents = []
        for i in range(2):
            w_water = w_wet[i] - w_dry[i]
            w_soil = w_dry[i] - w_cont[i]
            
            if w_soil <= 0:
                st.error(f"❌ Error in Trial {i+1}: Dry soil weight must be positive.")
                return
            
            water_contents.append((w_water / w_soil) * 100)
        
        pl_val = np.mean(water_contents)
        
        # Validation for consistency (Standard check: |w1 - w2| <= 1.0)
        diff = abs(water_contents[0] - water_contents[1])
                
        st.write("---")
        # Added the success message and session_state save here
        st.success(f"✅ Plastic Limit (PL) = {pl_val:.2f}%")
        st.session_state["pl_result"] = pl_val  # Save it for the Classification module
        
        st.metric(label="Calculated Plastic Limit (PL)", value=f"{pl_val:.2f}%")
        
        
        if diff > 1.0:
            st.warning(f"⚠️ Warning: High variation between trials (diff = {diff:.2f}%). Standard tolerance is 1.0%.")
        
        st.write(f"Trial 1: {water_contents[0]:.2f}% | Trial 2: {water_contents[1]:.2f}%")

    def reset_to_home():
        st.session_state.nav_choice = "Home"

    st.button("Back to Home", on_click=reset_to_home)

if __name__ == "__main__":
    run()
