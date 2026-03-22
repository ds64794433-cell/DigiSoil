import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("🌍 Natural Moisture Content Test (Oven Drying Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-2):1973")

    st.write("Enter the weights from the moisture content cans used for the field samples.")

    # 1. Initialize Table
    if "nmc_data" not in st.session_state:
        st.session_state.nmc_data = pd.DataFrame({
            "Wt. of Container (g)": [0.0, 0.0],
            "Wt. of Wet Soil + Cont. (g)": [0.0, 0.0],
            "Wt. of Dry Soil + Cont. (g)": [0.0, 0.0]
        })

    # Use a key to keep the editor state consistent
    edited_nmc_df = st.data_editor(st.session_state.nmc_data, num_rows="dynamic", key="nmc_editor_v2")

    if st.button("🚀 Calculate Natural Moisture", use_container_width=True):
        # 2. FIXED DATA CLEANING
        # Create a copy so we don't modify the session state directly during cleaning
        df_clean = edited_nmc_df.copy()
        
        # Columns to convert to numbers
        numeric_cols = ["Wt. of Container (g)", "Wt. of Wet Soil + Cont. (g)", "Wt. of Dry Soil + Cont. (g)"]
        
        for col in numeric_cols:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        # Remove rows that have any empty values in numeric columns
        df_clean = df_clean.dropna(subset=numeric_cols)

        if len(df_clean) < 1:
            st.error("❌ Please enter at least one complete row of numeric data.")
            return

        # 3. Calculation Logic
        w_cont = df_clean["Wt. of Container (g)"].values
        w_wet = df_clean["Wt. of Wet Soil + Cont. (g)"].values
        w_dry = df_clean["Wt. of Dry Soil + Cont. (g)"].values

        nmc_values = []
        for i in range(len(df_clean)):
            w_water = w_wet[i] - w_dry[i]
            w_soil = w_dry[i] - w_cont[i]
            
            if w_soil <= 0:
                st.warning(f"⚠️ Row {i+1}: Dry soil weight is zero or negative. Skipping.")
                continue
            
            nmc_values.append((w_water / w_soil) * 100)

        if not nmc_values:
            st.error("❌ No valid samples to calculate.")
            return

        # 4. Save Result to Session State
        nmc_avg = np.mean(nmc_values)
        st.session_state["nmc_result"] = nmc_avg
        st.success(f"✅ Average Natural Moisture Content (NMC) = **{nmc_avg:.2f}%**")

        # 5. Engineering Context (Liquidity Index)
        ll = st.session_state.get("liquid_limit_val", 0)
        pl = st.session_state.get("plastic_limit_val", 0)
        pi = st.session_state.get("pi_result", 0)

        # Check if Atterberg data exists AND PI is not zero
        if ll > 0 and pl > 0 and pi > 0:
            li = (nmc_avg - pl) / pi
            st.session_state["liquidity_index"] = li
            
            st.divider()
            st.subheader("📊 Consistency Analysis")
            col1, col2 = st.columns(2)
            
            # Now 'li' is guaranteed to exist here
            col1.metric("Liquidity Index (LI)", f"{li:.3f}")

            # --- Move the Interpretation INSIDE this block ---
            if li < 0:
                status = "Brittle / Semi-solid state"
            elif 0 <= li <= 1:
                status = "Plastic state"
            else:
                status = "Liquid state (High risk of flow)"
            
            col2.write(f"**Current State:** {status}")
        else:
            # If data is missing, show a helpful note instead of crashing
            st.info("💡 **Note:** Complete the Liquid and Plastic Limit tests to unlock the Liquidity Index analysis.")

# 6. Sidebar Sync (Optional but recommended)
if "nmc_result" in st.session_state:
    st.sidebar.success(f"NMC: {st.session_state.nmc_result:.1f}%")
