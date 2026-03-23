import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("🧪 Plastic Limit (PL) Determination")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-5):1985")

    # 1. INITIALIZE MASTER STORAGE
    if "pl_master_v4" not in st.session_state:
        st.session_state.pl_master_v4 = pd.DataFrame({
            "Container Wt (g)": [0.0, 0.0],
            "Wet Soil + Cont. (g)": [0.0, 0.0],
            "Dry Soil + Cont. (g)": [0.0, 0.0]
        }, index=["Trial 1", "Trial 2"])

    st.subheader("Laboratory Data Input")
    
    # 2. THE DATA EDITOR
    # We catch the output of the editor to ensure we get the latest numbers
    edited_df = st.data_editor(
        st.session_state.pl_master_v4, 
        num_rows="fixed", 
        use_container_width=True,
        key="pl_editor_v4" 
    )

    # 3. THE CALCULATION LOGIC
    if st.button("🚀 Calculate Plastic Limit", use_container_width=True):
        # Clean data for calculation from the editor output
        df_num = edited_df.apply(pd.to_numeric, errors='coerce')
        
        # Check for zeros or empty values
        if (df_num == 0).any().any():
            st.error("❌ Please fill all trial data with values greater than 0.")
        else:
            try:
                w_cont = df_num.iloc[:, 0].values
                w_wet = df_num.iloc[:, 1].values
                w_dry = df_num.iloc[:, 2].values
                
                water_contents = []
                for i in range(len(df_num)):
                    # --- PHYSICAL CHECKS ---
                    if w_dry[i] >= w_wet[i]:
                        st.error(f"❌ Trial {i+1}: Dry weight cannot be ≥ Wet weight.")
                        st.stop()
                    if w_cont[i] >= w_dry[i]:
                        st.error(f"❌ Trial {i+1}: Container weight cannot be ≥ Dry soil.")
                        st.stop()

                    w_water = w_wet[i] - w_dry[i]
                    w_soil = w_dry[i] - w_cont[i]
                    water_contents.append((w_water / w_soil) * 100)
                
                avg_pl = round(np.mean(water_contents), 2)
                
                # Update Session State
                st.session_state.pl_master_v4 = edited_df # Save the inputs
                st.session_state.plastic_limit_val = avg_pl
                st.session_state.pl_trials = water_contents
                
                st.success(f"✅ Plastic Limit Calculated: {avg_pl}%")
                st.rerun() 

            except Exception as e:
                st.error(f"❌ Calculation Error: {str(e)}")

    # --- 4. PERSISTENT DISPLAY ---
    # FIXED: Changed 'st.session' to 'st.session_state'
    if "plastic_limit_val" in st.session_state:
        st.divider()
        res = st.session_state.plastic_limit_val
        st.metric("Final Plastic Limit (PL)", f"{res}%")
        
        # Display the trial breakdown
        st.write("Trial Breakdown:")
        trial_data = pd.DataFrame({
            "Trial": ["Trial 1", "Trial 2"],
            "Water Content (%)": st.session_state.pl_trials
        })
        st.table(trial_data)

    # NAVIGATION
    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()
