import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# 1. Complete USCS Dictionary with Recommendations
USCS_DATA = {
    "GW": ("Well-graded gravel", "Excellent base material, good drainage."),
    "GP": ("Poorly graded gravel", "Possible voids, needs compaction control."),
    "GM": ("Silty gravel", "Fair foundation material, frost susceptible."),
    "GC": ("Clayey gravel", "Good base, low permeability, stable."),
    "SW": ("Well-graded sand", "Excellent foundation, good permeability."),
    "SP": ("Poorly graded sand", "Potential for liquefaction, requires compaction."),
    "SM": ("Silty sand", "Erosion prone, sensitive to moisture changes."),
    "SC": ("Clayey sand", "Good stability, low permeability."),
    "ML": ("Silt, low plasticity", "Frost susceptible, poor drainage."),
    "MH": ("Silt, high plasticity", "Highly compressible, poor foundation."),
    "CL": ("Clay, low plasticity", "Predictable, moderate shrink-swell."),
    "CH": ("Clay, high plasticity", "High expansion, requires stabilization."),
    "OL": ("Organic clay/silt, low plasticity", "Unsuitable for structural foundations."),
    "OH": ("Organic clay/silt, high plasticity", "Highly compressible, avoid for load-bearing."),
    "GW-GM": ("Well-graded gravel with silt", "Good stability, verify drainage."),
    "GP-GM": ("Poorly graded gravel with silt", "Requires drainage evaluation."),
    "GW-GC": ("Well-graded gravel with clay", "Very stable base material."),
    "GP-GC": ("Poorly graded gravel with clay", "Good base, check permeability."),
    "SW-SM": ("Well-graded sand with silt", "Good stability, moderate permeability."),
    "SP-SM": ("Poorly graded sand with silt", "Moderate stability, check compaction."),
    "SW-SC": ("Well-graded sand with clay", "Stable, low permeability."),
    "SP-SC": ("Poorly graded sand with clay", "Stable, check for voids."),
    "GC-GM": ("Clayey gravel with silt", "Mixed behavior, moderate permeability."),
    "SC-SM": ("Clayey sand with silt", "Mixed behavior, evaluate drainage."),
    "CL-ML": ("Silty clay (Dual symbol)", "Transition zone behavior, check plasticity."),
    "CI": ("Intermediate plasticity clay", "Stable if compacted properly."),
    "MI": ("Intermediate plasticity silt", "Monitor moisture closely.")
}

def create_pdf(data, symbol, desc, rec):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Comprehensive Soil Analysis Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for k, v in data.items(): pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Final Classification: {symbol}", ln=True)
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(200, 10, txt=f"Description: {desc}", ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Engineering Recommendation: {rec}")
    if os.path.exists("gsd_curve.png"): 
        pdf.ln(10)
        pdf.image("gsd_curve.png", x=10, y=None, w=150)

    # Inside create_pdf function
    if os.path.exists("gsd_curve.png"): 
        pdf.ln(10)
        pdf.image("gsd_curve.png", x=10, w=150)
    else:
        pdf.ln(10)
        pdf.cell(200, 10, txt="Note: GSD Curve not generated.", ln=True)

    return pdf.output(dest='S').encode('latin-1')

def run():
    st.header("Full Soil Classification (USCS)")
    
    # Retrieve data from session state
    ll = st.session_state.get("ll_result", 0.0)
    pi = st.session_state.get("pi_result", 0.0)
    fines = st.session_state.get("fines_result", 0.0)
    cu = st.session_state.get("cu_result", 0.0)
    cc = st.session_state.get("cc_result", 0.0)
    gravel = st.session_state.get("gravel_percent", 0.0) 
    sand = st.session_state.get("sand_percent", 0.0)

    if ll == 0 and pi == 0 and fines == 0:
        st.warning("⚠️ **Missing Data:** Please complete the GSD and Atterberg Limit tests first.")
        # We don't return here, we just show the warning so the user can still see the UI

    # Display Summary with 6 columns (Gravel and Sand added)
    st.write("### Measured Index Properties")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("LL", f"{ll:.1f}%")
    c2.metric("PI", f"{pi:.1f}%")
    c3.metric("Fines", f"{fines:.1f}%")
    c4.metric("Gravel", f"{gravel:.1f}%")
    c5.metric("Sand", f"{sand:.1f}%")
    c6.metric("Cu/Cc", f"{cu:.1f}/{cc:.1f}")

    if st.button("Generate Final Classification"):
        symbol = ""
        # 1. COARSE-GRAINED SOILS (Fines < 50%)
        if fines < 50:
            prefix = "G" if gravel > sand else "S"
            
            # Case A: Fines < 5%
            if fines < 5:
                well_graded = (cu >= 4 and 1 <= cc <= 3) if prefix == "G" else (cu >= 6 and 1 <= cc <= 3)
                symbol = f"{prefix}W" if well_graded else f"{prefix}P"
            
            # Case B: Fines > 12%
            elif fines > 12:
                a_line = 0.73 * (ll - 20)
                suffix = "C" if (pi > 7 and pi > a_line) else "M"
                symbol = f"{prefix}{suffix}"
            
            # Case C: Dual Symbols (5% to 12% Fines)
            else:
                well_graded = (cu >= 4 and 1 <= cc <= 3) if prefix == "G" else (cu >= 6 and 1 <= cc <= 3)
                a_line = 0.73 * (ll - 20)
                suffix = "C" if (pi > 7 and pi > a_line) else "M"
                grad_sym = "W" if well_graded else "P"
                symbol = f"{prefix}{grad_sym}-{prefix}{suffix}"

        # 2. FINE-GRAINED SOILS (Fines >= 50%)
        else:
            a_line = 0.73 * (ll - 20)
            if ll < 50:
                if pi > 7 and pi > a_line:
                    symbol = "CL"
                elif pi < 4 or pi < a_line:
                    symbol = "ML"
                else: 
                    symbol = "CL-ML" # The "Silty Clay" zone
            else:
                if pi > a_line:
                    symbol = "CH"
                else:
                    symbol = "MH"

        # Fetch description and recommendation
        desc, rec = USCS_DATA.get(symbol, ("Unknown", "Consult site-specific data."))
        
        st.divider()
        st.success(f"## Final Symbol: {symbol}")
        st.write(f"**Description:** {desc}")
        st.info(f"**Recommendation:** {rec}")

        # PDF Export - Updated to include Gravel and Sand in PDF
        report_data = {
            "Liquid Limit": f"{ll:.1f}%", 
            "Plasticity Index": f"{pi:.1f}%", 
            "Fines %": f"{fines:.1f}%",
            "Gravel %": f"{gravel:.1f}%",
            "Sand %": f"{sand:.1f}%",
            "Cu": f"{cu:.2f}", 
            "Cc": f"{cc:.2f}"
        }
        pdf_bytes = create_pdf(report_data, symbol, desc, rec)
        st.download_button(label="📥 Download PDF Report", data=pdf_bytes, file_name="Classification_Report.pdf", mime="application/pdf")

    if st.button("Back to Home"):
        st.session_state.nav_choice = "Home"
        st.rerun()

if __name__ == "__main__":
    run()
