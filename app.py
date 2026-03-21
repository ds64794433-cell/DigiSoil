import streamlit as st
import importlib
import os  # Fixed: Added missing import

# 1. Setup the Page Branding (The 'Face' of the app)
# Change 'icon.png' to your actual gallery filename
LOGO_FILE = "icon.png" 

st.set_page_config(
    page_title="DigiSoil '26",
    page_icon=LOGO_FILE if os.path.exists(LOGO_FILE) else "🏗️",
    layout="wide"
)

# Inject PWA Manifest for Mobile/Desktop Installation
st.markdown(
    f"""
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="{LOGO_FILE}">
    """,
    unsafe_allow_html=True
)

# --- Sidebar Start ---
with st.sidebar:
    # 1. Place the Logo at the VERY TOP
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.info("🏗️ DigiSoil Lab Automation")

    # 2. Place the Title right below it
    st.title("DigiSoil '26")
    
    # 3. Developer Info
    st.markdown(f"**Developer:** Diya Sharma")
    st.markdown("**(BTCE24O1027)**")
    st.markdown("**Dept:** Civil Engineering")
    st.markdown("**Institute:** MITS-DU GWALIOR")
    st.divider()

# --- In app.py Sidebar Section ---
st.sidebar.subheader("📊 Test Status")

# GSD uses 'fines_percent'
gsd_status = "✅" if "fines_percent" in st.session_state else "⚪"
st.sidebar.write(f"{gsd_status} Grain Size Analysis")

# LL uses 'liquid_limit_val'
ll_status = "✅" if "liquid_limit_val" in st.session_state else "⚪"
st.sidebar.write(f"{ll_status} Liquid Limit Test")

# PL uses 'plastic_limit_val'
pl_status = "✅" if "plastic_limit_val" in st.session_state else "⚪"
st.sidebar.write(f"{pl_status} Plastic Limit Test")

st.sidebar.divider()
options = ["Home"] + list(MODULES.keys())
current_idx = options.index(st.session_state.nav_choice) if st.session_state.nav_choice in options else 0
page = st.sidebar.radio("Navigation Menu", options, index=current_idx)

# 5. Main Dashboard UI
if page == "Home":
    st.markdown("<h1 class='main-title'>🏗️ DigiSoil Lab Automation</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>MITS-DU Gwalior | Soil Index Properties Automation</p>", unsafe_allow_html=True)
    st.divider()

    # Layout for 7 modules (using columns)
    modules_list = list(MODULES.keys())
    
    # Grid Logic: 4 on top, 3 on bottom for better balance
    row1 = st.columns(4)
    row2 = st.columns(3)
    cols = row1 + row2

    for i, mod in enumerate(modules_list):
        with cols[i]:
            st.markdown(f"""
                <div class="module-card">
                    <h2 style="margin: 0;">{MODULES[mod]['icon']}</h2>
                    <h5 style="margin: 5px 0;">{mod}</h5>
                    <p style="font-size: 0.8rem; opacity: 0.8;">{MODULES[mod]['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Open Test", key=f"btn_{mod}"):
                st.session_state.nav_choice = mod
                st.rerun()

else:
    # 6. Dynamic Module Loader
    mod_name = MODULES[page]["mod"]
    try:
        module = importlib.import_module(f"modules.{mod_name}")
        module.run()
        
            
    except Exception as e:
        st.error(f"❌ Error loading module: {e}")

