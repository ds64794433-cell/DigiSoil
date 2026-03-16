import streamlit as st

def run():
    st.header("Specific Gravity of Soil Solids")
    
    st.write("Enter the laboratory weights for the Pycnometer test.")

    # Using value=None and placeholder to ensure no default 0.0 values appear
    w1 = st.number_input("Weight of empty pycnometer (W1) [g]", min_value=0.0, step=0.01, value=None, placeholder="e.g., 50.00")
    w2 = st.number_input("Weight of pycnometer + dry soil (W2) [g]", min_value=0.0, step=0.01, value=None, placeholder="e.g., 100.00")
    w3 = st.number_input("Weight of pycnometer + soil + water (W3) [g]", min_value=0.0, step=0.01, value=None, placeholder="e.g., 150.00")
    w4 = st.number_input("Weight of pycnometer + water (W4) [g]", min_value=0.0, step=0.01, value=None, placeholder="e.g., 130.00")

    if st.button("Calculate Specific Gravity ($G_s$)"):
        # Check if all fields are populated
        if None in [w1, w2, w3, w4]:
            st.error("⚠️ Please fill in all four weight fields.")
            return

        # Specific Gravity calculation formula:
        # Gs = (W2 - W1) / ((W4 - W1) - (W3 - W2))
        
        numerator = w2 - w1
        denominator = (w4 - w1) - (w3 - w2)
        
        if denominator <= 0:
            st.error("❌ Calculation Error: The term ((W4-W1) - (W3-W2)) must be greater than zero. Please check your data.")
        else:
            gs = numerator / denominator
            st.success(f"### Calculated Specific Gravity ($G_s$): {gs:.3f}")
            st.info("Note: Typical values for soil solids range between 2.60 and 2.80.")

    # Navigation logic
    def reset_to_home():
        st.session_state.nav_choice = "Home"

    st.button("Back to Home", on_click=reset_to_home)

if __name__ == "__main__":
    run()
