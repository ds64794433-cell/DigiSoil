import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run():
    st.header("Plasticity Index Calculation")

    # 1. Initialize variables to avoid UnboundLocalError
    ll = st.session_state.get("ll_result", None)
    pl = st.session_state.get("pl_result", None)
    pi = None

    # Calculate PI if LL and PL exist
    if ll is not None and pl is not None:
        pi = ll - pl
        st.session_state["pi_result"] = pi
        st.success(f"Plasticity Index (PI) = {pi:.2f}%")
    else:
        st.warning("Please ensure Liquid Limit and Plastic Limit modules are calculated first.")

    # 2. Guard Clause: Only plot if we have valid data
    if ll is not None and pi is not None:
        st.subheader("Plasticity Chart")
        
        # Define A-Line (PI = 0.73 * (LL - 20))
        ll_range = np.linspace(0, 100, 100)
        a_line = 0.73 * (ll_range - 20)
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(ll_range, a_line, label="A-Line (PI = 0.73(LL-20))", color="red", linestyle="--")
        ax.scatter([ll], [pi], color="blue", s=100, label="Sample Point", zorder=5)
        
        ax.set_xlabel("Liquid Limit (LL)")
        ax.set_ylabel("Plasticity Index (PI)")
        ax.set_xlim(0, 100)
        ax.set_ylim(-5, 60)
        ax.legend()
        ax.grid(True)
        
        st.pyplot(fig)
        
        # Save for PDF report
        fig.savefig("plasticity_chart.png")
        plt.close(fig)
    else:
        st.info("Plasticity chart will appear here once data is calculated.")

    # 3. Navigation
    def reset_to_home():
        st.session_state.nav_choice = "Home"
    st.button("Back to Home", on_click=reset_to_home)

if __name__ == "__main__":
    run()
