import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("⚖️ Specific Gravity Test (Pycnometer Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-3):1980")

    # 1. Initialize Table Data
    if "gs_data_input" not in st.session_state:
        st.session_state.gs_data_input = pd.DataFrame({
            "W1": [0.0, 0.0], # Empty Pycnometer
            "W2": [0.0, 0.0], # Pycnometer + Dry Soil
            "W3": [0.0, 0.0], # Pycnometer + Soil + Water
            "W4": [0.0, 0.0]  # Pycnometer + Water
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
    edited_gs_df = st.data_editor(st.session_state.gs_data_input, num_rows="fixed", key="gs_editor")

    if st.button("🚀 Calculate Specific Gravity"):
        # Save edited data so it doesn't reset
        st.session_state.gs_data_input = edited_gs_df
        
        df_num = edited_gs_df.apply(pd.to_numeric, errors='coerce')
        w1, w2, w3, w4 = df_num["W1"].values, df_num["W2"].values, df_num["W3"].values, df_num["W4"].values

        gs_values = []
        for i in range(2):
            numerator = w2[i] - w1[i]
            denominator = (w2[i] - w1[i]) - (w3[i] - w4[i])
            
            if denominator == 0:
                st.error(f"❌ Trial {i+1}: Math error (Check your weights).")
                return
            gs_values.append(numerator / denominator)

        # --- SAVE TO SESSION STATE ---
        avg_gs = round(np.mean(gs_values), 3)
        st.session_state["gs_result"] = avg_gs 
        
        # Trigger Sidebar Update
        st.rerun()

    # --- 2. PERSISTENT RESULT DISPLAY (Outside the Button) ---
    if "gs_result" in st.session_state:
        gs_avg = st.session_state["gs_result"]
        
        st.write("---")
        st.success(f"✅ Specific Gravity ($G_s$) = **{gs_avg:.3f}**")

        col1, col2 = st.columns([1, 2])
        col1.metric("Final $G_s$", f"{gs_avg}")
        
        with col2:
            # Engineering Context
            if 2.60 <= gs_avg <= 2.80:
                st.info("💡 **Typical Range:** Consistent with standard quartz-based soils.")
            elif gs_avg < 2.60:
                st.warning("⚠️ **Note:** Low $G_s$ might indicate organic content.")
            else:
                st.warning("⚠️ **Note:** High $G_s$ indicates heavy minerals.")

    # --- NAVIGATION ---
    st.divider()
    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
    
