import streamlit as st
import pandas as pd

def run():
    st.header("Natural Moisture Content")
    
    # Input table for the test
    df_input = pd.DataFrame({
        "Container Wt (g)": [0.0],
        "Wet Soil + Cont. (g)": [0.0],
        "Dry Soil + Cont. (g)": [0.0]
    }, index=["Test Sample"])

    edited_df = st.data_editor(df_input, num_rows="fixed")

    if st.button("Calculate Moisture Content"):
        row = edited_df.iloc[0]
        w_water = row["Wet Soil + Cont. (g)"] - row["Dry Soil + Cont. (g)"]
        w_soil = row["Dry Soil + Cont. (g)"] - row["Container Wt (g)"]
        
        if w_soil <= 0:
            st.error("Invalid weight: Dry soil weight must be positive.")
        else:
            mc = (w_water / w_soil) * 100
            st.metric("Natural Moisture Content", f"{mc:.2f}%")

    if st.button("Back to Home", on_click=lambda: st.session_state.update(nav_choice="Home")):
        st.rerun()
