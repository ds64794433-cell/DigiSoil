import streamlit as st
import importlib

# 1. Page Configuration
st.set_page_config(
    page_title="DigiSoil | MITS-DU Gwalior", 
    page_icon="🏗️", 
    layout="wide"
)

if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Home"

# 2. Refined CSS (Snaps Button to Card)
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
    
    .main-title {
        text-align: center;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Module Registry (Liquid and Plastic Separated)
MODULES = {
    "Grain Size Analysis": {"mod": "gsd", "icon": "📊", "desc": "Sieve analysis & Gradation curves"},
    "Liquid Limit": {"mod": "liquid_limit", "icon": "💧", "desc": "Casagrande Method (IS 2720 P-5)"},
    "Plastic Limit": {"mod": "plastic_limit", "icon": "🧪", "desc": "3mm Thread Rolling Test"},
    "Plasticity Index": {"mod": "plasticity_index", "icon": "📉", "desc": "A-Line & IP Calculation"},
    "Natural Moisture Content": {"mod": "moisture_content", "icon": "🌡️", "desc": "Field Moisture, Oven Drying Method"},
    "Specific Gravity": {"mod": "specific_gravity", "icon": "⚖️", "desc": "Pycnometer method"},
    "Full Classification": {"mod": "full_classification", "icon": "📑", "desc": "Final IS 1498 Symbol Reporting"}
}

# 4. Sidebar Navigation
with st.sidebar:
    # 1. Place the Logo at the VERY TOP
    try:
        st.image("assets/mits_logo.png", width=80)
    except:
        st.info("Logo file not found in folder.")

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

