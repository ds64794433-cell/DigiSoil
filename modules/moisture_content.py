import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("🌍 Natural Moisture Content Test (Oven Drying Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-2):1973")

    # 1. INITIALIZE MASTER STORAGE (Using v4 for stability)
    if "nmc_master_v4" not in st.session_state:
        st.session_state.nmc_master_v4 = pd.DataFrame({
            "Wt. of Container (g)": [None, None],
            "Wt. of Wet Soil + Cont. (g)": [None, None],
            "Wt. of Dry Soil + Cont. (g)": [None, None]
        })

    st.subheader("Laboratory Data Input")
    
    # 2. THE DATA EDITOR (Isolated Buffer)
    # Using 'dynamic' so you can add more samples if needed
    st.data_editor(
        st.session_state.nmc_master_v4, 
        num_rows="dynamic", 
        use_container_width=True,
        key="nmc_editor_v4" 
    )

    # 3. THE CALCULATION LOGIC
    if st.button("🚀 Calculate Natural Moisture", use_container_width=True):
        # Access the widget's internal buffer
        raw_edits = st.session_state.nmc_editor_v4
        df = st.session_state.nmc_master_v4.copy()
        
        # --- MANUAL MERGE LOGIC ---
        # 1. Handle Edited Rows
        for row_idx, changes in raw_edits["edited_rows"].items():
            for col_name, new_val in changes.items():
                df.at[int(row_idx), col_name] = new_val
        
        # 2. Handle Added Rows
        for new_row in raw_edits["added_rows"]:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
        # 3. Handle Deleted Rows
        indices_to_drop = raw_edits["deleted_rows"]
        df = df.drop(indices_to_drop).reset_index(drop=True)
        
        # Save merged data back to state
        st.session_state.nmc_master_v4 = df
        
        # Clean data for calculation
        df_num = df.apply(pd.to_numeric, errors='coerce').dropna()
        
        if len(df_num) < 1:
            st.error("❌ Please enter at least one complete row of data.")
        else:
            try:
                w_cont = df_num.iloc[:, 0].values
                w_wet = df_num.iloc[:, 1].values
                w_dry = df_num.iloc[:, 2].values
                
                nmc_values = []
                for i in range(len(df_num)):
                    # --- PHYSICAL CHECKS ---
                    if w_dry[i] >= w_wet[i]:
                        st.error(f"❌ Row {i+1}: Dry weight cannot be ≥ Wet weight.")
                        return
                    if w_cont[i] >= w_dry[i]:
                        st.error(f"❌ Row {i+1}: Container weight cannot be ≥ Dry soil.")
                        return
                    if w_cont[i] <= 0 or w_wet[i] <= 0 or w_dry[i] <= 0:
                        st.error(f"❌ Row {i+1}: Weights must be positive.")
                        return

                    w_water = w_wet[i] - w_dry[i]
                    w_soil = w_dry[i] - w_cont[i]
                    nmc_values.append((w_water / w_soil) * 100)
                
                nmc_avg = round(np.mean(nmc_values), 2)
                
                # Final result check
                if nmc_avg <= 0:
                    st.error(f"❌ **Physical Error:** Average NMC is {nmc_avg}%. Moisture cannot be negative.")
                    return

                # Save Result
                st.session_state.nmc_result = nmc_avg
                st.success("✅ Natural Moisture Content Calculated!")
                st.rerun() 

            except Exception as e:
                st.error(f"❌ Calculation Error: {str(e)}")

    # --- 4. PERSISTENT DISPLAY & CONSISTENCY ANALYSIS ---
    if "nmc_result" in st.session_state:
        nmc_val = st.session_state.nmc_result
        st.write("---")
        st.success(f"✅ **Average NMC = {nmc_val}%**")

        # --- LIQUIDITY INDEX (LI) CALCULATION ---
        ll = st.session_state.get("liquid_limit_val", 0)
        pl = st.session_state.get("plastic_limit_val", 0)
        
        # We calculate PI on the fly to ensure accuracy
        pi = ll - pl

        if ll > 0 and pl > 0 and pi > 0:
            li = (nmc_val - pl) / pi
            st.session_state["liquidity_index"] = li
            
            st.subheader("📊 Consistency Analysis (Liquidity Index)")
            col1, col2 = st.columns(2)
            col1.metric("Liquidity Index (LI)", f"{li:.3f}")

            # Interpretation based on LI
            if li < 0:
                status = "Brittle / Semi-solid state"
                color = "blue"
            elif 0 <= li <= 1:
                status = "Plastic state"
                color = "green"
            else:
                status = "Liquid state (High risk of flow)"
                color = "red"
            
            col2.markdown(f"**Current State:** :{color}[{status}]")
        else:
            st.info("💡 **Note:** Complete the **Liquid Limit** and **Plastic Limit** tests to unlock the Liquidity Index analysis.")

    # --- 5. NAVIGATION ---
    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()
