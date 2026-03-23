import streamlit as st
import importlib
import os
import base64

def get_image_base64(path):
    """
    Converts an image file to a base64 string so it can be 
    displayed inside HTML tags in Streamlit.
    """
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
        return None
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

@st.dialog("Developer & Faculty Mentors")
def show_developer_info():
    # 1. UPDATED CSS FOR BETTER VISIBILITY
    st.markdown("""
        <style>
        .dev-header {
            display: flex;
            align-items: center;
            gap: 25px;
            margin-bottom: 20px;
            padding: 10px;
        }
        .dev-img-box {
            width: 150px;
            height: 170px;
            border-radius: 15px;
            overflow: hidden;
            border: 3px solid #FF4B2B;
            flex-shrink: 0;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        }
        .dev-img-box img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .dev-name-main {
            font-size: 2.2rem;
            font-weight: 900;
            color: #60A5FA; /* Brighter Blue for Dark Mode */
            line-height: 1.1;
            margin-bottom: 5px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        /* Style for the details text */
        .dev-details {
            font-size: 1rem;
            color: #E5E7EB; /* Off-white/Light gray */
            line-height: 1.5;
        }
        .dev-details strong {
            color: #FFA500; /* Orange highlight for titles */
        }
        .fac-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            text-align: center;
        }
        .fac-card {
            background: rgba(255, 255, 255, 0.05); /* Semi-transparent background */
            padding: 15px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .fac-name {
            font-weight: 800;
            font-size: 1.1rem;
            color: #FFFFFF; /* Pure white name */
        }
        .fac-title {
            color: #FF4B2B; /* Vibrant accent red */
            font-size: 0.8rem;
            font-weight: 700;
            margin-top: 4px;
        }
        .fac-dept {
            font-size: 0.75rem;
            color: #9CA3AF; /* Muted gray for secondary info */
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. THE DEVELOPER SECTION
    img_diya = get_image_base64("diyaa.jpeg")
    st.markdown(f"""
        <div class="dev-header">
            <div class="dev-img-box">
                <img src="data:image/jpeg;base64,{img_diya if img_diya else ''}">
            </div>
            <div class="dev-info-box">
                <div class="dev-name-main">Diya Sharma</div>
                <div class="dev-details">
                       (BTCE24O1027)<br>
                    🎓 2nd Year B.Tech (Civil Engineering)<br>
                    📍 <strong>Graphic Head</strong> | The Bhagwat Club<br>
                    🏆 <strong>8.6 CGPA</strong>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. THE FACULTY SECTION
    st.markdown("<p style='text-align: center; font-weight: 700; color: #9CA3AF;'>UNDER THE GUIDANCE OF</p>", unsafe_allow_html=True)
    
    img_mohit = get_image_base64("mohit_sir.jpg")
    img_sanjay = get_image_base64("sanjay_sir.webp")

    # Use this inside your fac-grid markdown to ensure photos are perfectly aligned
    st.markdown(f"""
        <div class="fac-grid">
            <div class="fac-card">
                <img src="data:image/jpeg;base64,{img_mohit if img_mohit else ''}" 
                     style="width:100%; height:160px; border-radius:10px; object-fit:cover;">
                <div class="fac-name">Dr. Mohit Kumar</div>
                <div class="fac-title">Assistant Professor</div>
                <div class="fac-dept">Department of Civil Engineering</div>
            </div>
            <div class="fac-card">
                <img src="data:image/webp;base64,{img_sanjay if img_sanjay else ''}" 
                     style="width:100%; height:160px; border-radius:10px; object-fit:cover;">
                <div class="fac-name">Dr. Sanjay Tiwari</div>
                <div class="fac-title">Prof. & Head</div>
                <div class="fac-dept">Department of Civil Engineering</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.info("✨ Developed at MITS-DU Gwalior to automate Geotechnical Laboratory analysis.")

# 1. Page Configuration
st.set_page_config(
    page_title="DigiSoil | MITS-DU Gwalior", 
    page_icon="🏗️", 
    layout="wide"
)

# Initialize navigation state
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Home"

# 2. Refined CSS
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

# 3. Module Registry (CRITICAL: Match your filenames in the 'modules' folder!)
MODULES = {
    "Grain Size Analysis": {"mod": "gsd", "icon": "📊", "desc": "Sieve analysis & Gradation curves"},
    "Liquid Limit": {"mod": "liquid_limit", "icon": "💧", "desc": "Casagrande Method (IS 2720 P-5)"},
    "Plastic Limit": {"mod": "plastic_limit", "icon": "🧪", "desc": "3mm Thread Rolling Test"},
    "Natural Moisture Content": {"mod": "moisture_content", "icon": "🌡️", "desc": "Field Moisture, Oven Drying Method"},
    "Specific Gravity": {"mod": "specific_gravity", "icon": "⚖️", "desc": "Pycnometer method"},
    "Plasticity Index": {"mod": "plasticity_index", "icon": "📉", "desc": "A-Line & IP Calculation"},
    "Full Classification": {"mod": "full_classification", "icon": "📑", "desc": "Final IS 1498 Symbol Reporting"}
}

# --- Sidebar Start ---
with st.sidebar:
    if os.path.exists("mits_logo.png"):
        st.image("mits_logo.png", width=120)
    else:
        st.info("🏗️ DigiSoil '26")

    st.title("DigiSoil '26")
    st.markdown(f"**Developer:** Diya Sharma")
    st.markdown("**(BTCE24O1027)**")
    st.markdown("**Dept:** Civil Engineering")
    st.markdown("**Institute:** MITS-DU GWALIOR")
    st.divider()
    
    # --- Add this inside 'with st.sidebar:' ---

    if st.button("👤 About the Developer", use_container_width=True):
        show_developer_info() # We will define this function below
    
    # 4. TEST STATUS (Synchronized with Module Session Keys)
    st.subheader("📊 Test Status")
    
    # Check if the 'gsd_final' dictionary exists in session state
    gsd_done = 'gsd_final' in st.session_state
    st.write(f"{'✅' if gsd_done else '⚪'} Grain Size")

    # Liquid Limit check (assuming you use 'll_final' or similar in that module)
    ll_done = 'liquid_limit_val' in st.session_state or 'll_final' in st.session_state
    st.write(f"{'✅' if ll_done else '⚪'} Liquid Limit")

    # Plastic Limit check
    pl_done = 'plastic_limit_val' in st.session_state or 'pl_final' in st.session_state
    st.write(f"{'✅' if pl_done else '⚪'} Plastic Limit")

    # Natural Moisture
    nmc_done = 'nmc_result' in st.session_state
    st.write(f"{'✅' if nmc_done else '⚪'} Natural Moisture")

    # Specific Gravity
    gs_done = 'gs_result' in st.session_state
    st.write(f"{'✅' if gs_done else '⚪'} Specific Gravity")
    
    st.divider()

    # 5. NAVIGATION MENU
    options = ["Home"] + list(MODULES.keys())
    # This prevents the radio button from resetting your page choice
    page = st.radio("Navigation Menu", options, index=options.index(st.session_state.nav_choice))
    st.session_state.nav_choice = page

# --- Main Dashboard UI ---
if page == "Home":
    st.markdown("<h1 class='main-title'>🏗️ DigiSoil Lab Automation</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>MITS-DU Gwalior | Soil Index Properties Automation</p>", unsafe_allow_html=True)
    st.divider()

    # Grid Layout
    modules_list = list(MODULES.keys())
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
            
            # Key logic: Buttons update nav_choice and rerun the app
            if st.button(f"Open Test", key=f"btn_{mod}"):
                st.session_state.nav_choice = mod
                st.rerun()

else:
    # 6. Dynamic Module Loader
    mod_name = MODULES[page]["mod"]
    try:
        # Assumes your files are in a folder named 'modules'
        module = importlib.import_module(f"modules.{mod_name}")
        module.run()
    except Exception as e:
        st.error(f"❌ Error loading module '{mod_name}': {e}")
        st.info("Check if the file exists in the 'modules' folder.")
