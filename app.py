import streamlit as st
import importlib
import os

# --- 1. APP IDENTITY ---
# This is for the "Face" of the app (the gallery image you want as the desktop icon)
GALLERY_ICON = "icon.png" 

st.set_page_config(
    page_title="DigiSoil '26",
    page_icon=GALLERY_ICON if os.path.exists(GALLERY_ICON) else "🏗️",
    layout="wide"
)

# Inject PWA Manifest for the Desktop/Phone Icon
st.markdown(f"""
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="{GALLERY_ICON}">
""", unsafe_allow_html=True)

# --- 2. YOUR ORIGINAL CSS (Restored) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, rgba(30,58,138,0.05) 0%, rgba(255,75,43,0.05) 100%);
    }
    .module-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px 15px 0 0; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: 5px solid #FF4B2B;
        text-align: center;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    div.stButton > button {
        background-color: #FF4B2B !important;
        color: white !important;
        border-radius: 0 0 15px 15px !important; 
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        height: 42px !important;
        margin-top: -5px !important; 
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #1E3A8A !important;
        transform: translateY(2px);
    }
    .main-title { text-align: center; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- 3. MODULE REGISTRY ---
MODULES = {
    "Grain Size Analysis": {"mod": "gsd", "icon": "📊", "desc": "Sieve analysis & Gradation curves"},
    "Liquid Limit": {"mod": "liquid_limit", "icon": "💧", "desc": "Casagrande Method (IS 2720 P-5)"},
    "Plastic Limit": {"mod": "plastic_limit", "icon": "🧪", "desc": "3mm Thread Rolling Test"},
    "Plasticity Index": {"mod": "plasticity_index", "icon": "📉", "desc": "A-Line & IP Calculation"},
    "Natural Moisture Content": {"mod": "moisture_content", "icon": "🌡️", "desc": "Field Moisture, Oven Drying Method"},
    "Specific Gravity": {"mod": "specific_gravity", "icon": "⚖️", "desc": "Pycnometer method"},
    "Full Classification": {"mod": "full_classification", "icon": "📑", "desc": "Final IS 1498 Symbol Reporting"}
}

if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Home"

# --- 4. SIDEBAR (With corrected Logo Logic) ---
with st.sidebar:
    # TRY TO SHOW YOUR GALLERY LOGO FIRST
    if os.path.exists(GALLERY_ICON):
        st.image(GALLERY_ICON, use_container_width=True)
    # FALLBACK TO THE ASSETS LOGO IF ACCIDENTALLY RENAMED
    elif os.path.exists("assets/mits_logo.png"):
        st.image("assets/mits_logo.png", width=100)
    else:
        st.info("🏗️ DigiSoil Lab Automation")

    st.title("DigiSoil '26")
    st.markdown("**Developer:** Diya Sharma\n**(BTCE24O1027)**\n\n**Dept:** Civil Engineering\n**Institute:** MITS-DU GWALIOR")
    st.divider()

    st.subheader("📊 Test Status")
    st.write(f"{'✅' if 'fines_percent' in st.session_state else '⚪'} Grain Size Analysis")
    st.write(f"{'✅' if 'liquid_limit_val' in st.session_state else '⚪'} Liquid Limit Test")
    st.write(f"{'✅' if 'plastic_limit_val' in st.session_state else '⚪'} Plastic Limit Test")
    st.divider()

    options = ["Home"] + list(MODULES.keys())
    page = st.sidebar.radio("Navigation Menu", options, index=options.index(st.session_state.nav_choice))

# --- 5. MAIN DASHBOARD ---
if page == "Home":
    st.markdown("<h1 class='main-title'>🏗️ DigiSoil Lab Automation</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>MITS-DU Gwalior | Soil Index Properties Automation</p>", unsafe_allow_html=True)
    st.divider()

    row1 = st.columns(4)
    row2 = st.columns(3)
    cols = row1 + row2

    for i, mod in enumerate(list(MODULES.keys())):
        with cols[i]:
            st.markdown(f"""
                <div class="module-card">
                    <h2 style="margin: 0;">{MODULES[mod]['icon']}</h2>
                    <h5 style="margin: 5px 0;">{mod}</h5>
                    <p style="font-size: 0.8rem; opacity: 0.8;">{MODULES[mod]['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Test", key=f"btn_{mod}"):
                st.session_state.nav_choice = mod
                st.rerun()
else:
    try:
        module = importlib.import_module(f"modules.{MODULES[page]['mod']}")
        module.run()
    except Exception as e:
        st.error(f"❌ Error loading module: {e}")
