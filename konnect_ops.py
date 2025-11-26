import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KonnectOps Mobile",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. HIGH-CONTRAST CSS (Black Text Fix) ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* FORCE GLOBAL BLACK TEXT */
        html, body, [class*="css"], h1, h2, h3, h4, p, span, label, div {
            font-family: 'Segoe UI', sans-serif;
            color: #000000 !important; /* Force Black Text */
        }
        
        /* APP BACKGROUND (Light Gray) */
        .stApp {
            background-color: #f4f6f9 !important;
        }
        
        /* HIDE DEFAULT BRANDING */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* --- INPUT FIELDS (High Contrast) --- */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
            font-size: 16px !important; /* Mobile Readable */
        }
        
        /* --- BUTTONS (Home Konnect Blue) --- */
        .stButton>button {
            width: 100%;
            background-color: #002D62 !important;
            color: #ffffff !important; /* White text ONLY on buttons */
            border-radius: 8px;
            height: 3.5em;
            font-weight: bold;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button:hover {
            background-color: #001a3d !important;
        }
        
        /* --- CARDS & CONTAINERS --- */
        .element-container, .stDataFrame {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 5px;
        }

        /* --- LOCKED SCREEN BOX --- */
        .locked-box {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            margin: 50px auto;
            max-width: 90%;
            border-top: 6px solid #002D62;
        }
        
        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #e0e0e0;
            padding: 10px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: white;
            border-radius: 5px;
            color: #000000 !important;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #002D62 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = None

# --- 4. CONNECTION HELPER ---
def try_connect(key):
    try:
        genai.configure(api_key=key)
        models = list(genai.list_models())
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
        return models[0].name if models else None
    except:
        return None

# --- 5. AI HELPER ---
def ask_ai(prompt):
    if not st.session_state.model_name: return "Error: Offline"
    try:
        model = genai.GenerativeModel(st.session_state.model_name)
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Error: {e}"

# --- 6. SIDEBAR (Reset Option) ---
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("Logout"):
        st.session_state.api_key = ""
        st.session_state.model_name = None
        st.rerun()

# --- 7. MAIN LOGIC ---

# Attempt Connection
if st.session_state.api_key and not st.session_state.model_name:
    model_id = try_connect(st.session_state.api_key)
    if model_id:
        st.session_state.model_name = model_id
        st.rerun()
    else:
        st.error("❌ Invalid Key")
        st.session_state.api_key = ""

# === VIEW 1: LOCKED SCREEN ===
if not st.session_state.model_name:
    st.markdown("""
    <div class="locked-box">
        <i class="fa-solid fa-lock" style="font-size: 50px; color: #002D62; margin-bottom: 20px;"></i>
        <h2 style="color: #000000 !important;">KonnectOps Login</h2>
        <p style="color: #333333 !important; font-size: 16px;">Secure Digital Operations Center</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔑 Enter API Key")
    key_input = st.text_input("Paste Key Here", type="password", label_visibility="collapsed")
    
    if st.button("🚀 Unlock Dashboard"):
        if key_input:
            st.session_state.api_key = key_input
            st.rerun()
        else:
            st.warning("Please paste your key.")

# === VIEW 2: DASHBOARD ===
else:
    st.markdown(f"### <i class='fa-solid fa-rocket' style='color:#002D62'></i> Digital HQ", unsafe_allow_html=True)
    st.caption(f"🟢 Online: {st.session_state.model_name.split('/')[-1]}")

    # TABS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Landing Page", 
        "✍️ Content", 
        "🎨 Images", 
        "📅 Calendar",
        "👨‍💻 Zoho"
    ])

    # --- TAB 1: LANDING PAGE ---
    with tab1:
        st.markdown("#### <i class='fa-solid fa-code'></i> Developer Console", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            proj = st.text_input("Project Name", placeholder="TVS Emerald")
            loc = st.text_input("Location", placeholder="Porur")
            price = st.text_input("Price", placeholder="85L")
        with c2:
            old_txt = st.text_input("Old Name", value="Casagrand Flagship")
            html = st.text_area("Paste HTML Code", height=150)
        
        if st.button("⚡ Generate Page"):
            if html:
                res = html.replace(old_txt, proj).replace("{PRICE}", price).replace("{LOCATION}", loc)
                with st.spinner("Optimizing SEO..."):
                    seo = ask_ai(f"Write 150 char SEO description for {proj} in {loc}.")
                    if "{DESC}" in res: res = res.replace("{DESC}", seo)
                st.download_button("Download HTML", res, f"{proj}.html")

    # --- TAB 2: CONTENT ---
    with tab2:
        st.markdown("#### <i class='fa-solid fa-pen-nib'></i> Marketing Studio", unsafe_allow_html=True)
        ctype = st.selectbox("Content Type", ["Instagram Carousel", "LinkedIn Post", "Client Email"])
        topic = st.text_input("Topic", placeholder="Why invest in OMR?")
        if st.button("✨ Draft Content"):
            with st.spinner("Writing..."):
                st.write(ask_ai(f"Act as Marketing Manager. Write a {ctype} about {topic}."))

    # --- TAB 3: IMAGES ---
    with tab3:
        st.markdown("#### <i class='fa-solid fa-palette'></i> Image Prompts", unsafe_allow_html=True)
        desc = st.text_input("Image Concept", placeholder="Luxury living room with sea view")
        if st.button("🎨 Generate Prompt"):
            st.code(ask_ai(f"Write a detailed Midjourney prompt for: {desc}"))

    # --- TAB 4: CALENDAR ---
    with tab4:
        st.markdown("#### <i class='fa-regular fa-calendar'></i> 2026 Festivals", unsafe_allow_html=True)
        data = {
            "Date": ["Jan 14", "Jan 26", "Mar 04", "Mar 20", "Apr 14", "Aug 15", "Aug 26", "Sep 14", "Oct 20", "Nov 08", "Dec 25"],
            "Festival": ["Pongal", "Republic Day", "Holi", "Ramzan", "Tamil New Year", "Independence Day", "Onam", "Ganesh Chaturthi", "Ayudha Puja", "Diwali", "Christmas"]
        }
        st.table(pd.DataFrame(data))

    # --- TAB 5: ZOHO ---
    with tab5:
        st.markdown("#### <i class='fa-solid fa-terminal'></i> Deluge Scripting", unsafe_allow_html=True)
        req = st.text_area("Logic Needed", placeholder="e.g. Update lead status when email opens")
        if st.button("Compile Code"):
            with st.spinner("Coding..."):
                st.code(ask_ai(f"Write Zoho Deluge script: {req}"), language='java')
