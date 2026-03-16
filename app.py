import streamlit as st
import importlib

# 1. Page Configuration
st.set_page_config(
    page_title="Soil Lab Suite", 
    page_icon="🌱", 
    layout="wide"
)

# 2. Module Registry
MODULES = {
    "Grain Size Analysis": {"mod": "gsd", "icon": "📊"},
    "Liquid Limit": {"mod": "liquid_limit", "icon": "💧"},
    "Plastic Limit": {"mod": "plastic_limit", "icon": "🧪"},
    "Plasticity Index": {"mod": "plasticity_index", "icon": "📉"},
    "Natural Moisture Content": {"mod": "moisture_content", "icon": "🌡️"},
    "Specific Gravity": {"mod": "specific_gravity", "icon": "⚖️"},
    "Full Soil Classification": {"mod": "full_classification", "icon": "📑"}
}

# 3. Sidebar Navigation & State Sync
st.sidebar.title("🌱 Soil Lab Suite")
st.sidebar.markdown("---")

if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Home"

# Create options list and safely find the index
options = ["Home"] + list(MODULES.keys())
current_idx = options.index(st.session_state.nav_choice) if st.session_state.nav_choice in options else 0

# Sidebar Radio
page = st.sidebar.radio("Select Module", options, index=current_idx)

# Sync sidebar selection with session state
if page != st.session_state.nav_choice:
    st.session_state.nav_choice = page
    st.rerun()

# 4. Main Dashboard UI
if page == "Home":
    st.title("Soil Index Property Automation")
    st.subheader("Select a test from the library to begin analysis")
    st.markdown("---")
    
    # Create a clean grid layout
    cols = st.columns(3)
    modules_list = list(MODULES.keys())
    
    for i, mod in enumerate(modules_list):
        with cols[i % 3]:
            # Professional container layout
            with st.container():
                st.write(f"### {MODULES[mod]['icon']} {mod}")
                if st.button(f"Open Test", key=f"btn_{mod}", use_container_width=True):
                    st.session_state.nav_choice = mod
                    st.rerun()
                st.write("") # Spacer

    st.markdown("---")

else:
    # 5. Dynamic Module Loader
    mod_name = MODULES[page]["mod"]
    try:
        module = importlib.import_module(f"modules.{mod_name}")
        module.run()
    except Exception as e:
        st.error(f"Could not load module '{mod_name}': {e}")