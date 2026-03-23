import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("⚖️ Specific Gravity Test (Pycnometer Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-3):1980")

    # 1. INITIALIZE MASTER STORAGE (Using v4 for stability)
    if "gs_master_v4" not in st.session_state:
        st.session_state.gs_master_v4 = pd.DataFrame({
            "W1 (Empty)": [None, None],
            "W2 (Pyc+Soil)": [None, None],
            "W3 (Pyc+Soil+Water)": [None, None],
            "W4 (Pyc+Water)": [None, None]
        }, index=["Trial 1", "Trial 2"])

    # Legend for the Engineering Students
    with st.expander("📚 View Weight Definitions (Legend)"):
        st.markdown("""
        * **W1**: Weight of Empty Pycnometer (g)
        * **W2**: Weight of Pycnometer + Dry Soil (g)
        * **W3**: Weight of Pycnometer + Soil + Water (g)
        * **W4**: Weight of Pycnometer + Water (g)
        """)

    st.subheader("Laboratory Data Input")
    
    # 2. THE DATA EDITOR (Isolated Buffer)
    st.data_editor(
        st.session_state.gs_master_v4, 
        num_rows="fixed", 
        use_container_width=True,
        key="gs_editor_v4" 
    )

    # 3. THE CALCULATION LOGIC
    if st.button("🚀 Calculate Specific Gravity", use_container_width=True):
        # Access the widget's internal buffer
        raw_edits = st.session_state.gs_editor_v4
        df = st.session_state.gs_master_v4.copy()
        
        # --- MANUAL MERGE ---
        for row_idx, changes in raw_edits["edited_rows"].items():
            row_key = row_idx if row_idx in df.index else list(df.index)[int(row_idx)]
            for col_name, new_val in changes.items():
                df.at[row_key, col_name] = new_val
        
        st.session_state.gs_master_v4 = df
        df_num = df.apply(pd.to_numeric, errors='coerce').dropna()

        if len(df_num) < 2:
            st.error("❌ Please fill all rows for both trials.")
        else:
            try:
                w1 = df_num.iloc[:, 0].values
                w2 = df_num.iloc[:, 1].values
                w3 = df_num.iloc[:, 2].values
                w4 = df_num.iloc[:, 3].values

                gs_values = []
                for i in range(len(df_num)):
                    # --- PHYSICAL CHECKS ---
                    # Logic: W3 (Soil+Water) must be heavier than W4 (Water only)
                    # Logic: W2 (Pyc+Soil) must be heavier than W1 (Empty)
                    if w2[i] <= w1[i]:
                        st.error(f"❌ {df_num.index[i]}: W2 must be greater than W1 (Dry soil weight error).")
                        return
                    if w3[i] <= w4[i]:
                        st.error(f"❌ {df_num.index[i]}: W3 must be greater than W4 (Displaced water error).")
                        return
                    if (w2[i]-w1[i]) <= (w3[i]-w4[i]):
                        st.error(f"❌ {df_num.index[i]}: Internal weight inconsistency. Result would be negative/infinite.")
                        return

                    numerator = w2[i] - w1[i]
                    denominator = (w2[i] - w1[i]) - (w3[i] - w4[i])
                    
                    gs_trial = numerator / denominator
                    gs_values.append(gs_trial)

                avg_gs = round(np.mean(gs_values), 3)

                # --- CHECK: Gs SHOULD NOT BE NEGATIVE OR UNREALISTIC ---
                if avg_gs <= 0:
                    st.error(f"❌ **Physical Error:** Calculated $G_s$ is {avg_gs}. Check your weights.")
                    return
                if avg_gs > 5.0:
                    st.error(f"❌ **Unrealistic Result:** $G_s$ of {avg_gs} is too high for soil. Check your inputs.")
                    return

                # Save to state
                st.session_state["gs_result"] = avg_gs
                st.success("✅ Specific Gravity Calculated!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Calculation Error: {str(e)}")

    # --- 4. PERSISTENT RESULT DISPLAY ---
    if "gs_result" in st.session_state:
        gs_avg = st.session_state["gs_result"]
        
        st.write("---")
        st.success(f"✅ Final Specific Gravity ($G_s$) = **{gs_avg:.3f}**")

        col1, col2 = st.columns([1, 2])
        col1.metric("Resulting $G_s$", f"{gs_avg}")
        
        with col2:
            if 2.60 <= gs_avg <= 2.80:
                st.info("💡 **Standard Range:** Normal for inorganic soils.")
            elif gs_avg < 2.60:
                st.warning("⚠️ **Note:** Potential Organic Soil or Peat.")
            else:
                st.warning("⚠️ **Note:** Likely contains heavy minerals (e.g., Iron).")

    # --- 5. NAVIGATION ---
    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()
