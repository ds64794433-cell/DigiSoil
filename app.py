import streamlit as st
import importlib
import os

# --- 1. APP IDENTITY & FACE ---
# Ensure this filename matches your GitHub upload exactly!
LOGO_FILE = "icon.png" 

st.set_page_config(
    page_title="DigiSoil '26",
    page_icon=LOGO_FILE if os.path.exists(LOGO_FILE) else "🏗️",
    layout="wide"
)

# This makes your gallery image the 'Face' for home-screen installation
st.markdown(
    f"""
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="{LOGO_FILE}">
    """,
    unsafe_allow_html=True
)

# --- 2. MODULE REGISTRY (Must be defined before the sidebar uses it!) ---
MODULES = {
    "Grain Size Analysis": {"mod": "gsd", "icon": "📊", "desc": "Sieve analysis & Gradation curves"},
    "Liquid Limit": {"mod": "liquid_limit", "icon": "💧", "desc": "Casagrande Method (IS 2720 P-5)"},
    "Plastic Limit": {"mod": "plastic_limit", "icon": "🧪", "desc": "3mm Thread Rolling Test"},
    "Plasticity Index": {"mod": "plasticity_index", "icon": "📉", "desc": "A-Line & IP Calculation"},
    "Natural Moisture Content": {"mod": "moisture_content", "icon": "🌡️", "desc": "Field Moisture, Oven Drying Method"},
    "Specific Gravity": {"mod": "specific_gravity", "icon": "⚖️", "desc": "Pycnometer method"},
    "Full Classification": {"mod": "full_classification", "icon": "📑", "desc": "Final IS 1498 Symbol Reporting"}
}

# --- 3. SESSION STATE ---
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Home"

# --- 4. SIDEBAR UI ---
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.info("🏗️ DigiSoil Lab Automation")

    st.title("DigiSoil '26")
    st.markdown(f"**Developer:** Diya Sharma\n**(BTCE24O1027)**")
    st.markdown("**Dept:** Civil Engineering\n**Institute:** MITS-DU GWALIOR")
    st.divider()

    # Test Status Indicators
    st.subheader("📊 Test Status")
    gsd_status = "✅" if "fines_percent" in st.session_state else "⚪"
    st.write(f"{gsd_status} Grain Size Analysis")
    
    ll_status = "✅" if "liquid_limit_val" in st.session_state else "⚪"
    st.write(f"{ll_status} Liquid Limit Test")
    
    pl_status = "✅" if "plastic_limit_val" in st.session_state else "⚪"
    st.write(f"{pl_status} Plastic Limit Test")
    
    st.divider()

    # Navigation Menu (This will now work because MODULES is defined above!)
    options = ["Home"] + list(MODULES.keys())
    current_idx = options.index(st.session_state.nav_choice) if st.session_state.nav_choice in options else 0
    page = st.sidebar.radio("Navigation Menu", options, index=current_idx)

# --- 5. MAIN DASHBOARD ---
if page == "Home":
    st.markdown("<h1 style='text-align: center;'>🏗️ DigiSoil Lab Automation</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>MITS-DU Gwalior | Soil Index Properties Automation</p>", unsafe_allow_html=True)
    st.divider()

    # Layout for cards
    row1 = st.columns(4)
    row2 = st.columns(3)
    cols = row1 + row2

    for i, mod in enumerate(list(MODULES.keys())):
        with cols[i]:
            st.info(f"### {MODULES[mod]['icon']} {mod}")
            st.caption(MODULES[mod]['desc'])
            if st.button(f"Open Test", key=f"btn_{mod}"):
                st.session_state.nav_choice = mod
                st.rerun()
else:
    # Module Loader
    mod_name = MODULES[page]["mod"]
    try:
        module = importlib.import_module(f"modules.{mod_name}")
        module.run()
    except Exception as e:
        st.error(f"❌ Error loading module: {e}")
