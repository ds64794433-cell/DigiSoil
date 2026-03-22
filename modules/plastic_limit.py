import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("🧪 Plastic Limit (PL) Determination")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    # 1. Initialize Table Data
    if "pl_data_input" not in st.session_state:
        st.session_state.pl_data_input = pd.DataFrame({
            "Container Wt (g)": [0.0, 0.0],
            "Wet Soil + Cont. (g)": [0.0, 0.0],
            "Dry Soil + Cont. (g)": [0.0, 0.0]
        }, index=["Trial 1", "Trial 2"])

    st.subheader("Laboratory Data")
    edited_df = st.data_editor(st.session_state.pl_data_input, num_rows="fixed", key="pl_editor")

    if st.button("🚀 Calculate Plastic Limit"):
        # Save edited data back to session state
        st.session_state.pl_data_input = edited_df
        
        df_num = edited_df.apply(pd.to_numeric, errors='coerce')
        w_cont = df_num["Container Wt (g)"].values
        w_wet = df_num["Wet Soil + Cont. (g)"].values
        w_dry = df_num["Dry Soil + Cont. (g)"].values
        
        water_contents = []
        for i in range(2):
            w_water = w_wet[i] - w_dry[i]
            w_soil = w_dry[i] - w_cont[i]
            if w_soil <= 0:
                st.error(f"❌ Trial {i+1}: Dry soil weight must be positive.")
                return
            water_contents.append((w_water / w_soil) * 100)
        
        # --- SAVE RESULTS ---
        avg_pl = round(np.mean(water_contents), 2)
        st.session_state["plastic_limit_val"] = avg_pl
        st.session_state["pl_trials"] = water_contents
        
        # Trigger immediate sidebar update
        st.rerun() 

    # --- PERSISTENT DISPLAY (Outside Button) ---
    if "plastic_limit_val" in st.session_state:
        pl_val = st.session_state["plastic_limit_val"]
        trials = st.session_state.get("pl_trials", [0, 0])
        
        st.write("---")
        st.success(f"✅ Plastic Limit (PL) = **{pl_val}%**")
        
        col1, col2 = st.columns(2)
        col1.metric("Resulting PL", f"{pl_val}%")
        
        diff = abs(trials[0] - trials[1])
        if diff > 1.0:
            st.warning(f"⚠️ High variation: {diff:.2f}%. Standard limit is 1.0%.")
            
        st.info(f"Trial 1: {trials[0]:.2f}% | Trial 2: {trials[1]:.2f}%")

    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
