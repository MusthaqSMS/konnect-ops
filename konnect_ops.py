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

# --- 2. MOBILE-FIRST CSS ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Global Font */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
        
        /* APP BACKGROUND */
        .stApp {
            background: #f0f2f6;
        }
        
        /* HIDE STREAMLIT BRANDING (But keep functionality) */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* --- INPUT FIELDS (Mobile Friendly) --- */
        .stTextInput input {
            font-size: 16px !important; /* Prevents iPhone Zoom */
            padding: 12px !important;
            border-radius: 8px !important;
            border: 1px solid #cbd5e1 !important;
        }
        
        /* --- BUTTONS --- */
        .stButton>button {
            width: 100%;
            background-color: #002D62;
            color: white;
            border-radius: 8px;
            height: 3.5em;
            font-weight: bold;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* --- LOCKED SCREEN CARD --- */
        .locked-box {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin: 20px auto;
            max-width: 400px;
            border-top: 5px solid #002D62;
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
        # Pick the best available model
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
        return models[0].name if models else None
    except:
        return None

# --- 5. SIDEBAR (Settings) ---
with st.sidebar:
    st.header("⚙️ Settings")
    # Allow resetting key from sidebar if needed
    if st.button("Logout / Reset Key"):
        st.session_state.api_key = ""
        st.session_state.model_name = None
        st.rerun()

# --- 6. MAIN LOGIC ---

# Attempt Connection if Key Exists
if st.session_state.api_key and not st.session_state.model_name:
    model_id = try_connect(st.session_state.api_key)
    if model_id:
        st.session_state.model_name = model_id
        st.rerun()
    else:
        st.error("❌ Invalid Key. Please try again.")
        st.session_state.api_key = "" # Reset on failure

# === VIEW 1: LOCKED SCREEN (LOGIN) ===
if not st.session_state.model_name:
    st.markdown("""
    <div class="locked-box">
        <i class="fa-solid fa-lock" style="font-size: 40px; color: #002D62;"></i>
        <h2 style="color: #333;">KonnectOps Login</h2>
        <p style="color: #666; font-size: 14px;">Secure Digital Operations Center</p>
    </div>
    """, unsafe_allow_html=True)
    
    # BIG CENTRAL INPUT (No Sidebar Needed)
    st.markdown("### 🔑 Enter Credentials")
    key_input = st.text_input("Paste Google API Key", type="password", placeholder="AIza...", label_visibility="collapsed")
    
    if st.button("🚀 Login to Dashboard"):
        if key_input:
            st.session_state.api_key = key_input
            st.rerun()
        else:
            st.warning("⚠️ Please paste your key first.")

    st.markdown("<br><center><small>Don't have a key? <a href='https://aistudio.google.com/app/apikey'>Get one here</a></small></center>", unsafe_allow_html=True)

# === VIEW 2: DASHBOARD (UNLOCKED) ===
else:
    # Header
    st.markdown(f"### <i class='fa-solid fa-rocket' style='color:#002D62'></i> Digital HQ", unsafe_allow_html=True)
    st.caption(f"🟢 System Online: {st.session_state.model_name.split('/')[-1]}")
    
    # AI Function
    def ask_ai(prompt):
        try:
            model = genai.GenerativeModel(st.session_state.model_name)
            return model.generate_content(prompt).text
        except Exception as e:
            return f"Error: {e}"

    # Tabs
    tabs = st.tabs(["📄 Page Builder", "✍️ Content", "🎨 Images", "📅 Calendar"])

    # Tab 1: Landing Page
    with tabs[0]:
        st.info("Build Landing Pages")
        proj = st.text_input("Project Name", placeholder="TVS Emerald")
        loc = st.text_input("Location", placeholder="Porur")
        price = st.text_input("Price", placeholder="85L")
        old_txt = st.text_input("Old Name (to replace)", value="Casagrand Flagship")
        html = st.text_area("Paste HTML Code", height=150)
        
        if st.button("⚡ Generate HTML"):
            if html:
                new_html = html.replace(old_txt, proj).replace("{PRICE}", price).replace("{LOCATION}", loc)
                with st.spinner("AI Optimizing..."):
                    seo = ask_ai(f"Write 150 char SEO description for {proj} in {loc}.")
                    if "{DESC}" in new_html: new_html = new_html.replace("{DESC}", seo)
                st.download_button("Download File", new_html, f"{proj}.html")

    # Tab 2: Content
    with tabs[1]:
        st.info("Generate Marketing Copy")
        ctype = st.selectbox("Type", ["Instagram Caption", "LinkedIn Post", "Email Reply"])
        topic = st.text_input("Topic", placeholder="e.g. Why buy in OMR?")
        if st.button("✨ Draft Content"):
            with st.spinner("Writing..."):
                st.write(ask_ai(f"Write a {ctype} about {topic}. Professional tone."))

    # Tab 3: Images
    with tabs[2]:
        st.info("AI Image Prompts")
        desc = st.text_input("Image Idea", placeholder="Luxury living room")
        if st.button("🎨 Get Prompt"):
            st.code(ask_ai(f"Write a Midjourney prompt for: {desc}"))

    # Tab 4: Calendar
    with tabs[3]:
        st.caption("2026 Festivals")
        data = {
            "Date": ["Jan 14", "Jan 26", "Mar 04", "Mar 20", "Apr 14", "Aug 15", "Aug 26", "Sep 14", "Oct 20", "Nov 08", "Dec 25"],
            "Festival": ["Pongal", "Republic Day", "Holi", "Ramzan", "Tamil New Year", "Independence Day", "Onam", "Ganesh Chaturthi", "Ayudha Puja", "Diwali", "Christmas"]
        }
        st.table(pd.DataFrame(data))
