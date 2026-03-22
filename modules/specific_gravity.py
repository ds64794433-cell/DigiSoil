import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.header("⚖️ Specific Gravity Test (Pycnometer Method)")
    st.info("DigiSoil | MITS-DU GWALIOR | IS:2720(Part-3):1980")

    st.write("Enter the observed weights from the Pycnometer test.")

    # 1. Initialize Table - CLEANED COLUMN NAMES
    if "gs_data" not in st.session_state:
        st.session_state.gs_data = pd.DataFrame({
            "W1": [None, None], # Wt. of Empty Pycnometer (g)
            "W2": [None, None], # Wt. of Pycnometer + Dry Soil (g)
            "W3": [None, None], # Wt. of Pycnometer + Soil + Water (g)
            "W4": [None, None]  # Wt. of Pycnometer + Water (g)
        })

    # Helping the user with a legend
    st.markdown("""
    **Legend:**
    * **W1**: Empty Pycnometer 
    * **W2**: Pycnometer + Dry Soil 
    * **W3**: Pycnometer + Soil + Water 
    * **W4**: Pycnometer + Water
    """)

    st.subheader("Laboratory Data Input")
    edited_gs_df = st.data_editor(st.session_state.gs_data, num_rows="fixed", key="gs_editor")

    if st.button("🚀 Calculate Specific Gravity"):
        # 2. Clean and Convert Data
        df_clean = edited_gs_df.dropna(how='any')
        df_clean = df_clean.apply(pd.to_numeric, errors='coerce').dropna()

        if len(df_clean) < 1:
            st.error("❌ Please fill at least one complete row.")
            return

        # Using the clean short names prevents "KeyErrors"
        w1 = df_clean["W1"].values
        w2 = df_clean["W2"].values
        w3 = df_clean["W3"].values
        w4 = df_clean["W4"].values

        # 3. Calculation Logic
        # Formula: Gs = (W2 - W1) / ((W2 - W1) - (W3 - W4))
        gs_values = []
        for i in range(len(df_clean)):
            numerator = w2[i] - w1[i]
            denominator = (w2[i] - w1[i]) - (w3[i] - w4[i])
            
            if denominator == 0:
                st.error(f"❌ Trial {i+1}: Math error (Denominator is 0). Check your weights.")
                return
            
            gs_values.append(numerator / denominator)

        # 4. Final Result
        gs_avg = np.mean(gs_values)
        st.session_state["gs_result"] = gs_avg # This saves it to the "brain" for the sidebar
        
        st.success(f"✅ Average Specific Gravity ($G_s$) = **{gs_avg:.3f}**")
        st.balloons()

        # 5. Engineering Context
        st.divider()
        if 2.60 <= gs_avg <= 2.80:
            st.info("💡 **Typical Range:** Consistent with standard quartz-based soils.")
        elif gs_avg < 2.60:
            st.warning("⚠️ **Note:** Low $G_s$ might indicate organic content.")
        else:
            st.warning("⚠️ **Note:** High $G_s$ indicates heavy minerals.")

    if st.button("🏠 Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()
