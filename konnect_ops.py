import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import logging
from functools import lru_cache
from urllib.parse import quote_plus
import streamlit.components.v1 as components
from typing import Optional

# ---------------------------
# Basic logging config
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("konnectops")

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="KonnectOps Mobile",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------
# HIGH-CONTRAST CSS (Fixed for Global Streamlit Scope)
# ---------------------------
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Global Font & Black Text Enforcement */
        html, body, [class*="css"], h1, h2, h3, h4, p, span, label, div {
            font-family: 'Segoe UI', sans-serif;
            color: #000000 !important; /* Force Black Text for Visibility */
        }

        /* APP BACKGROUND */
        .stApp {
            background-color: #f4f6f9 !important;
        }

        /* HIDE DEFAULT BRANDING */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* INPUT FIELDS */
        .stTextInput input, .stTextArea textarea, 
        .stSelectbox div[data-baseweb="select"], .stNumberInput input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
            font-size: 16px !important;
        }

        /* BUTTONS (Home Konnect Blue) */
        .stButton>button {
            width: 100%;
            background-color: #002D62 !important;
            color: #ffffff !important;
            border-radius: 8px;
            height: 3.5em;
            font-weight: bold;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button:hover {
            background-color: #001a3d !important;
        }

        /* CARDS & CONTAINERS */
        .element-container, .stDataFrame {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 5px;
        }

        /* LOCKED SCREEN BOX */
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

        /* TABS */
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
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# SESSION STATE
# ---------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""  # only kept in memory for current browser session
if "model_name" not in st.session_state:
    st.session_state.model_name = None
if "available_models" not in st.session_state:
    st.session_state.available_models = []
if "last_ai_error" not in st.session_state:
    st.session_state.last_ai_error = ""

# ---------------------------
# Helper: Cached model list fetcher
# ---------------------------
@lru_cache(maxsize=1)
def fetch_models_for_key(key: str):
    """
    Fetch models using the provided API key. Cached to reduce network calls.
    """
    try:
        genai.configure(api_key=key)
        models = list(genai.list_models() or [])
        logger.info("Fetched %d models", len(models))
        return models
    except Exception as e:
        logger.exception("Error fetching models: %s", e)
        raise

def safe_model_name_from_obj(obj) -> Optional[str]:
    """Extract a model name from returned model object/dict safely."""
    if obj is None:
        return None
    # try attribute access then mapping
    name = None
    try:
        name = getattr(obj, "name", None)
    except Exception:
        name = None
    if not name and isinstance(obj, dict):
        name = obj.get("name")
    return name

def model_supports_generate(obj) -> bool:
    """Return True if the model object advertises supported_generation_methods including generateContent."""
    try:
        methods = getattr(obj, "supported_generation_methods", None)
        if methods is None and isinstance(obj, dict):
            methods = obj.get("supported_generation_methods", None)
        if not methods:
            return False
        return "generateContent" in methods or "generate" in methods
    except Exception:
        return False

# ---------------------------
# Connection helper
# ---------------------------
def try_connect(key: str) -> Optional[str]:
    """
    Try connecting with key and select a reasonable model name.
    Returns model name if successful, else None.
    """
    if not key:
        return None
    try:
        models = fetch_models_for_key(key)
    except Exception as e:
        st.error("Could not fetch models. Check your API key or network.")
        logger.error("Model discovery failed: %s", e)
        return None

    # find a model that supports generateContent-like method
    for m in models:
        try:
            if model_supports_generate(m):
                name = safe_model_name_from_obj(m)
                if name:
                    # Prefer Flash models if available
                    if 'flash' in name and 'legacy' not in name:
                        st.session_state.available_models = [safe_model_name_from_obj(x) for x in models if safe_model_name_from_obj(x)]
                        return name
        except Exception:
            continue

    # fallback to first model if no explicit support found or no flash found
    if models:
        name = safe_model_name_from_obj(models[0])
        st.session_state.available_models = [safe_model_name_from_obj(x) for x in models if safe_model_name_from_obj(x)]
        return name
    return None

# ---------------------------
# AI Helper
# ---------------------------
def ask_ai(prompt: str) -> str:
    """
    Ask the configured Generative Model to produce text.
    Returns text or error string. Keeps the exception visible for debugging.
    """
    if not st.session_state.get("model_name"):
        return "Error: Offline (no model configured)."
    try:
        model = genai.GenerativeModel(st.session_state.model_name)
        
        # --- BRAND PERSONA INJECTION ---
        persona_prompt = f"""
        ROLE: Act as a Senior Digital Marketing Executive and Full Stack Developer for 'Home Konnect' (Chennai Real Estate).
        TONE: Professional, Authoritative, Persuasive, and SEO-Optimized.
        TASK: {prompt}
        """
        
        result = model.generate_content(persona_prompt)
        
        # The actual text property may vary; handle robustly
        text = getattr(result, "text", None)
        if not text and isinstance(result, dict):
            text = result.get("text") or str(result)
        if not text:
            text = str(result)
        return text
    except Exception as e:
        st.session_state.last_ai_error = str(e)
        logger.exception("AI call failed: %s", e)
        return f"Error (AI): {e}"

# ---------------------------
# Sidebar: Settings + Logout
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.caption("Key stored in session only.")
    
    if st.button("Logout / Clear Key"):
        # clear everything sensitive
        st.session_state.api_key = ""
        st.session_state.model_name = None
        st.session_state.available_models = []
        st.session_state.last_ai_error = ""
        try:
            fetch_models_for_key.cache_clear()
        except Exception:
            pass
        st.rerun()

# ---------------------------
# Attempt connection (if user provided key and not yet connected)
# ---------------------------
if st.session_state.api_key and not st.session_state.model_name:
    with st.spinner("Discovering available models..."):
        model_id = try_connect(st.session_state.api_key)
        if model_id:
            st.session_state.model_name = model_id
            st.success("Connected!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("❌ Invalid Key or model discovery failed.")
            # Reset key to allow retry
            st.session_state.api_key = "" 

# ---------------------------
# Locked view when not connected
# ---------------------------
if not st.session_state.model_name:
    st.markdown(
        """
        <div class="locked-box">
            <i class="fa-solid fa-lock" style="font-size: 50px; color: #002D62; margin-bottom: 20px;"></i>
            <h2 style="color: #000000 !important;">KonnectOps Login</h2>
            <p style="color: #333333 !important; font-size: 16px;">Secure Digital Operations Center</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🔑 Enter API Key")
    key_input = st.text_input("Paste Key Here", type="password", label_visibility="collapsed")
    
    if st.button("🚀 Unlock Dashboard"):
        if key_input:
            st.session_state.api_key = key_input
            st.rerun()
        else:
            st.warning("Please paste your key.")

else:
    # MAIN DASHBOARD
    st.markdown(f"### <i class='fa-solid fa-rocket' style='color:#002D62'></i> Digital HQ", unsafe_allow_html=True)
    st.caption(f"🟢 Online: {st.session_state.model_name.split('/')[-1]}")

    # tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📄 Landing Page", "✍️ Content", "🎨 Images", "📅 Calendar", "🛠️ Utilities", "👨‍💻 Zoho"]
    )

    # ---------------------------
    # TAB 1: LANDING PAGE
    # ---------------------------
    with tab1:
        st.markdown("#### <i class='fa-solid fa-code'></i> Developer Console", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            proj = st.text_input("Project Name", placeholder="TVS Emerald")
            loc = st.text_input("Location", placeholder="Porur")
            price = st.text_input("Price", placeholder="85L")
        with c2:
            old_txt = st.text_input("Old Name", value="Casagrand Flagship")
            html = st.text_area("Paste HTML Code", height=160, placeholder="<html>... use {PRICE}, {LOCATION}, {DESC}</html>")

        if st.button("⚡ Generate Page"):
            if not html:
                st.warning("Paste your HTML in the editor first.")
            else:
                try:
                    res = html.replace(old_txt or "", proj or "")
                    res = res.replace("{PRICE}", price or "")
                    res = res.replace("{LOCATION}", loc or "")
                    
                    # ask AI to write SEO only if {DESC} present
                    if "{DESC}" in res:
                        with st.spinner("Optimizing SEO..."):
                            seo = ask_ai(f"Write a 150 character SEO description for {proj or 'this project'} in {loc or ''}.")
                            if seo and not seo.lower().startswith("error"):
                                res = res.replace("{DESC}", seo)
                            else:
                                res = res.replace("{DESC}", f"{proj or ''} in {loc or ''} — premium homes.")
                except Exception as e:
                    st.error(f"Error processing HTML: {e}")
                    res = None

                if res:
                    # show preview safely
                    st.markdown("**Preview (rendered):**")
                    try:
                        components.html(res, height=400, scrolling=True)
                    except:
                        st.warning("Preview unavailable.")

                    # download button
                    st.download_button("Download HTML", data=res, file_name=f"{(proj or 'page')}.html", mime="text/html")

    # ---------------------------
    # TAB 2: CONTENT (Marketing Studio)
    # ---------------------------
    with tab2:
        st.markdown("#### <i class='fa-solid fa-pen-nib'></i> Marketing Studio", unsafe_allow_html=True)
        ctype = st.selectbox("Content Type", ["Blog Post", "Instagram Carousel", "LinkedIn Post", "Client Email"])
        topic = st.text_input("Topic", placeholder="Why invest in OMR?")
        
        if st.button("✨ Draft Content"):
            if not topic.strip():
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Writing..."):
                    prompt = f"Act as a Senior Marketing Manager. Write a {ctype} about: {topic}."
                    out = ask_ai(prompt)
                    st.code(out, language="text")

    # ---------------------------
    # TAB 3: IMAGES (Prompt generator)
    # ---------------------------
    with tab3:
        st.markdown("#### <i class='fa-solid fa-palette'></i> Image Prompts", unsafe_allow_html=True)
        desc = st.text_input("Image Concept", placeholder="Luxury living room with sea view")
        style = st.selectbox("Style", ["Photorealistic 8k", "Oil painting", "Flat vector"], index=0)
        if st.button("🎨 Generate Prompt"):
            if not desc.strip():
                st.warning("Enter an image concept.")
            else:
                prompt = f"Write a detailed Midjourney prompt for: {desc}. Style: {style}."
                with st.spinner("Generating prompt..."):
                    out = ask_ai(prompt)
                    st.code(out, language="text")

    # ---------------------------
    # TAB 4: CALENDAR
    # ---------------------------
    with tab4:
        st.markdown("#### <i class='fa-regular fa-calendar'></i> 2026 Festivals", unsafe_allow_html=True)
        data = {
            "Date": ["Jan 14", "Jan 26", "Mar 04", "Mar 20", "Apr 14", "Aug 15", "Aug 26", "Sep 14", "Oct 20", "Nov 08", "Dec 25"],
            "Festival": [
                "Pongal", "Republic Day", "Holi", "Ramzan", "Tamil New Year", 
                "Independence Day", "Onam", "Ganesh Chaturthi", "Ayudha Puja", 
                "Diwali", "Christmas"
            ],
        }
        st.table(pd.DataFrame(data))

    # ---------------------------
    # TAB 5: UTILITIES
    # ---------------------------
    with tab5:
        st.markdown("#### <i class='fa-solid fa-screwdriver-wrench'></i> Sales Tools", unsafe_allow_html=True)
        tool = st.radio("Select Tool:", ["WhatsApp Link Generator", "EMI Calculator", "Tamil Translator"], horizontal=True)

        if tool == "WhatsApp Link Generator":
            st.caption("Create pre-filled WhatsApp links for campaigns.")
            wa_num = st.text_input("Phone Number (with code)", "919876543210")
            wa_msg = st.text_input("Message", "Hi, I am interested in the OMR project.")
            if st.button("Generate WhatsApp Link"):
                if wa_num:
                    encoded_msg = quote_plus(wa_msg)
                    link = f"https://wa.me/{wa_num.strip()}?text={encoded_msg}"
                    st.code(link, language="text")
                    st.markdown(f"[Click to Test Link]({link})")

        elif tool == "EMI Calculator":
            st.caption("Quick Monthly Payment Estimator")
            loan = st.number_input("Loan Amount (₹)", value=5_000_000, step=100000)
            rate = st.number_input("Interest Rate (%)", value=8.5, step=0.1)
            years = st.number_input("Tenure (Years)", value=20, step=1)
            show_table = st.checkbox("Show amortization table", value=False)
            
            if st.button("Calculate EMI"):
                if loan > 0 and rate > 0 and years > 0:
                    r = rate / (12 * 100)
                    n = int(years * 12)
                    emi = loan * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
                    st.success(f"💰 Monthly EMI: ₹ {int(round(emi)):,}")
                    
                    if show_table:
                        bal = loan
                        rows = []
                        for m in range(1, n + 1):
                            interest = bal * r
                            principal = emi - interest
                            bal = bal - principal
                            rows.append((m, int(emi), int(principal), int(interest), int(max(bal, 0))))
                            if m >= 36 and n > 36 and not st.session_state.get("show_full_table"):
                                break
                        
                        df = pd.DataFrame(rows, columns=["Month", "EMI", "Principal", "Interest", "Balance"])
                        st.dataframe(df)
                        if n > 36:
                            st.caption("Showing first 3 years.")

        elif tool == "Tamil Translator":
            st.caption("English to Tamil for Local Ads")
            txt_to_translate = st.text_area("Enter English Text", "Exclusive launch offer ending soon.")
            if st.button("Translate"):
                with st.spinner("Translating..."):
                    st.code(ask_ai(f"Translate this real estate text to professional Tamil: '{txt_to_translate}'"), language="text")

    # ---------------------------
    # TAB 6: ZOHO
    # ---------------------------
    with tab6:
        st.markdown("#### <i class='fa-solid fa-terminal'></i> Deluge Scripting", unsafe_allow_html=True)
        req = st.text_area("Logic Needed", placeholder="e.g. Update lead status when email opens")
        if st.button("Compile Code"):
            with st.spinner("Coding..."):
                st.code(ask_ai(f"Write Zoho Deluge script: {req}"), language="java")
