import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import logging
from functools import lru_cache
from urllib.parse import quote_plus
import streamlit.components.v1 as components
from typing import Optional
import base64
import os
from io import BytesIO
import json

# --- OPTIONAL CLOUD IMPORTS ---
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from google.cloud import storage as gcs_storage
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

# ---------------------------
# LOGGING & CONFIG
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("konnectops")

st.set_page_config(
    page_title="KonnectOps Mobile",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------
# HTML BLOG TEMPLATES
# ---------------------------
TEMPLATE_QUICK = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{TITLE}</title>
  <meta name="description" content="{META_DESC}">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: 'Segoe UI', sans-serif; margin:0; padding:0; background:#f4f6f9; color:#111; }
    .hero { background: url('{COVER_URL}') center/cover no-repeat; height:360px; display:flex; align-items:center; position: relative; }
    .hero::after { content: ''; position: absolute; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.4); }
    .hero .title { position: relative; z-index: 2; color:#fff; padding:18px 28px; margin-left:24px; }
    .container { max-width:1000px; margin:28px auto; padding:0 18px; background: white; border-radius: 8px; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    h1 { font-size:32px; margin:0; }
    h2 { font-size:24px; margin:20px 0 10px; color: #002D62; }
    ul { margin-left:18px; line-height: 1.6; }
    p { line-height: 1.6; color: #444; }
    .cta { background:#002D62; color:#fff; padding:12px 24px; display:inline-block; border-radius:50px; text-decoration:none; font-weight: bold; margin-top: 20px; }
    .cta:hover { background: #004080; }
  </style>
</head>
<body>
  <section class="hero"><div class="title"><h1>{TITLE}</h1></div></section>
  <div class="container">
    <p><strong>Preview:</strong> {PREVIEW}</p>
    <h2>Introduction</h2>
    <p>{INTRO}</p>
    <h2>Highlights</h2>
    <ul>{HIGHLIGHTS}</ul>
    <h2>Location</h2>
    <p>{LOCATION_ADV}</p>
    <h2>Amenities</h2>
    <ul>{AMENITIES}</ul>
    <h2>Contact</h2>
    <p>Call: <a href="tel:{PHONE}">{PHONE}</a></p>
    <a href="https://wa.me/{PHONE}?text={WA_TEXT}" class="cta">Chat on WhatsApp</a>
  </div>
</body>
</html>
"""

TEMPLATE_LONGFORM = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{TITLE}</title>
  <meta name="description" content="{META_DESC}">
  <style>
    body { font-family: Georgia, serif; margin:0; padding:0; background:#fff; color:#333; line-height: 1.8; }
    header { padding:40px 20px; text-align: center; background:#f8f9fa; border-bottom:1px solid #eee; }
    .cover { width:100%; height:400px; background: url('{COVER_URL}') center/cover no-repeat; margin-bottom: 40px; }
    .content { max-width:800px; margin:0 auto; padding:40px 20px; }
    h1 { font-family: 'Arial', sans-serif; font-size:36px; margin-bottom: 10px; color: #111; }
    h2 { font-family: 'Arial', sans-serif; font-size:26px; margin-top: 40px; color: #002D62; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .meta { color:#666; font-style: italic; font-size: 14px; }
    .highlight-box { background: #f0f7ff; padding: 20px; border-left: 4px solid #002D62; margin: 30px 0; }
    .cta-button { display: block; width: 100%; max-width: 300px; margin: 40px auto; text-align: center; background: #d32f2f; color: white; padding: 15px; text-decoration: none; font-weight: bold; border-radius: 5px; font-family: sans-serif; }
  </style>
</head>
<body>
  <header>
    <h1>{TITLE}</h1>
    <p class="meta">{META_DESC}</p>
  </header>
  <div class="content">
    <div class="cover"></div>
    <div class="highlight-box"><strong>Quick Take:</strong> {PREVIEW}</div>
    <h2>The Vision</h2>
    <p>{INTRO}</p>
    <h2>Key Features</h2>
    <ul>{HIGHLIGHTS}</ul>
    <h2>Location & Connectivity</h2>
    <p>{LOCATION_ADV}</p>
    <h2>Premium Specifications</h2>
    <p>{SPECS}</p>
    <h2>Lifestyle Amenities</h2>
    <ul>{AMENITIES}</ul>
    <h2>About {DEVELOPER}</h2>
    <p>{DEVELOPER_BLURB}</p>
    <a class="cta-button" href="mailto:{EMAIL}">Download Brochure Now</a>
    <p style="text-align:center; font-size: 0.9rem;">Or call us at <a href="tel:{PHONE}">{PHONE}</a></p>
  </div>
</body>
</html>
"""

# ---------------------------
# HIGH-CONTRAST CSS (Fixed for Mobile)
# ---------------------------
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* FORCE BLACK TEXT GLOBAL */
        html, body, [class*="css"], h1, h2, h3, h4, p, span, label, div {
            font-family: 'Segoe UI', sans-serif;
            color: #000000 !important;
        }
        
        /* APP BACKGROUND */
        .stApp { background-color: #f4f6f9 !important; }
        
        /* HIDE BRANDING */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* INPUT FIELDS */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
            font-size: 16px !important;
        }
        
        /* BUTTONS */
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
        
        /* CARDS */
        .element-container, .stDataFrame {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 5px;
        }

        /* LOCKED SCREEN */
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
        .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #e0e0e0; padding: 10px; border-radius: 10px; }
        .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 5px; color: #000000 !important; font-weight: 600; }
        .stTabs [aria-selected="true"] { background-color: #002D62 !important; color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# STATE & HELPERS
# ---------------------------
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "model_name" not in st.session_state: st.session_state.model_name = None
if "s3_access" not in st.session_state: st.session_state.s3_access = ""
if "s3_secret" not in st.session_state: st.session_state.s3_secret = ""
if "s3_region" not in st.session_state: st.session_state.s3_region = ""
if "gcs_json" not in st.session_state: st.session_state.gcs_json = ""
if "_last_cover_bytes" not in st.session_state: st.session_state["_last_cover_bytes"] = None

@lru_cache(maxsize=1)
def fetch_models(key):
    genai.configure(api_key=key)
    return list(genai.list_models())

def try_connect(key):
    try:
        models = fetch_models(key)
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
        return models[0].name if models else None
    except: return None

def ask_ai(prompt):
    if not st.session_state.model_name: return "Error: Offline"
    try:
        model = genai.GenerativeModel(st.session_state.model_name)
        return model.generate_content(prompt).text
    except Exception as e: return f"Error: {e}"

def generate_image_bytes(prompt):
    # Best effort image generation via GenAI
    try:
        if hasattr(genai, "images") and hasattr(genai.images, "generate"):
            resp = genai.images.generate(model="image-alpha-001", prompt=prompt)
            if hasattr(resp, "data") and resp.data:
                b64 = resp.data[0].b64_json
                if b64: return base64.b64decode(b64)
    except: pass
    return None

def upload_s3(data, bucket, key):
    if not BOTO3_AVAILABLE: return "Error: boto3 not installed"
    try:
        s3 = boto3.client("s3", region_name=st.session_state.s3_region, aws_access_key_id=st.session_state.s3_access, aws_secret_access_key=st.session_state.s3_secret)
        s3.put_object(Bucket=bucket, Key=key, Body=data, ACL="public-read", ContentType="image/jpeg")
        return f"https://{bucket}.s3.{st.session_state.s3_region}.amazonaws.com/{key}"
    except Exception as e: return f"Error: {e}"

def upload_gcs(data, bucket_name, blob_name):
    if not GCS_AVAILABLE: return "Error: google-cloud-storage not installed"
    try:
        creds = service_account.Credentials.from_service_account_info(json.loads(st.session_state.gcs_json))
        client = gcs_storage.Client(credentials=creds)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data, content_type="image/jpeg")
        blob.make_public()
        return blob.public_url
    except Exception as e: return f"Error: {e}"

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Cloud Config Expander
    with st.expander("☁️ Cloud Upload Config"):
        st.caption("AWS S3")
        st.session_state.s3_access = st.text_input("Access Key", value=st.session_state.s3_access)
        st.session_state.s3_secret = st.text_input("Secret Key", type="password", value=st.session_state.s3_secret)
        st.session_state.s3_region = st.text_input("Region", value=st.session_state.s3_region)
        st.markdown("---")
        st.caption("Google Cloud")
        st.session_state.gcs_json = st.text_area("Service Account JSON", value=st.session_state.gcs_json)

    if st.button("Logout / Clear"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ---------------------------
# MAIN LOGIC
# ---------------------------
if st.session_state.api_key and not st.session_state.model_name:
    model = try_connect(st.session_state.api_key)
    if model:
        st.session_state.model_name = model
        st.rerun()
    else:
        st.error("Invalid Key")
        st.session_state.api_key = ""

if not st.session_state.model_name:
    st.markdown("""<div class="locked-box"><h2>KonnectOps Login</h2><p>Secure Digital Operations Center</p></div>""", unsafe_allow_html=True)
    key_input = st.text_input("Enter API Key", type="password")
    if st.button("🚀 Login"):
        st.session_state.api_key = key_input
        st.rerun()
else:
    st.markdown(f"### <i class='fa-solid fa-rocket' style='color:#002D62'></i> Digital HQ", unsafe_allow_html=True)
    st.caption(f"🟢 Online: {st.session_state.model_name}")

    tabs = st.tabs(["📄 Landing Page", "✍️ Content", "🎨 Images", "📅 Calendar", "🛠️ Utilities", "📝 Blog Builder", "☁️ Uploads", "👨‍💻 Zoho"])

    # 1. LANDING PAGE
    with tabs[0]:
        st.info("Developer Console")
        c1, c2 = st.columns(2)
        with c1:
            proj = st.text_input("Project", "TVS Emerald")
            loc = st.text_input("Location", "Porur")
            price = st.text_input("Price", "85L")
        with c2:
            old = st.text_input("Placeholder", "Casagrand Flagship")
            html = st.text_area("HTML Code", height=100)
        if st.button("⚡ Generate"):
            if html:
                res = html.replace(old, proj).replace("{PRICE}", price).replace("{LOCATION}", loc)
                st.download_button("Download HTML", res, f"{proj}.html")

    # 2. CONTENT
    with tabs[1]:
        st.info("Marketing Studio")
        ctype = st.selectbox("Type", ["Blog Post", "Social Media", "Email"])
        topic = st.text_input("Topic", "Why invest in OMR?")
        if st.button("Draft"):
            with st.spinner("Writing..."):
                st.code(ask_ai(f"Write a {ctype} about {topic}."), language="text")

    # 3. IMAGES
    with tabs[2]:
        st.info("Prompt Engineer")
        desc = st.text_input("Concept", "Luxury living room")
        if st.button("Get Prompt"):
            st.code(ask_ai(f"Write a Midjourney prompt for: {desc}"), language="text")

    # 4. CALENDAR
    with tabs[3]:
        st.info("2026 Festivals")
        data = {"Date": ["Jan 14", "Aug 15", "Nov 08", "Dec 25"], "Event": ["Pongal", "Independence Day", "Diwali", "Christmas"]}
        st.table(pd.DataFrame(data))

    # 5. UTILITIES
    with tabs[4]:
        st.info("Tools")
        tool = st.radio("Tool", ["WhatsApp Link", "EMI Calc"])
        if tool == "WhatsApp Link":
            num = st.text_input("Number", "919876543210")
            if st.button("Generate"): st.code(f"https://wa.me/{num}")
        else:
            loan = st.number_input("Loan", 5000000)
            if st.button("Calc EMI"): st.success(f"EMI: {int(loan * 0.008)}") # Simple approx for demo

    # 6. BLOG BUILDER (NEW)
    with tabs[5]:
        st.markdown("#### 📝 Blog Generator & Templates")
        
        b_col1, b_col2 = st.columns([2, 1])
        with b_col1:
            b_proj = st.text_input("Blog Project", "DRA Beena Clover")
            b_loc = st.text_input("Blog Location", "Madambakkam")
            b_usp = st.text_input("USPs", "Near Selaiyur, Value Pricing")
            b_img_url = st.text_input("Cover Image URL (Optional)", "")
        with b_col2:
            tmpl = st.selectbox("Template", ["Quick Template", "Long Form"])
            if st.button("Load Template"):
                t = TEMPLATE_QUICK if tmpl == "Quick Template" else TEMPLATE_LONGFORM
                filled = t.format(
                    TITLE=f"{b_proj} in {b_loc}", META_DESC=f"Premium homes in {b_loc}", 
                    COVER_URL=b_img_url or "https://via.placeholder.com/1200",
                    PREVIEW=f"Discover {b_proj}.", INTRO=f"Welcome to {b_proj} by DRA.",
                    HIGHLIGHTS=f"<li>{b_usp}</li>", LOCATION_ADV="Prime location.",
                    AMENITIES="<li>Gym</li>", PHONE="919876543210", EMAIL="sales@hk.com",
                    SPECS="Premium fittings.", DEVELOPER_BLURB="Trusted developer.", DEVELOPER="DRA",
                    WA_TEXT="Hi"
                )
                st.session_state["blog_html"] = filled
        
        # Editor
        blog_content = st.text_area("Blog HTML Editor", value=st.session_state.get("blog_html", ""), height=300)
        st.download_button("Download Blog HTML", blog_content, "blog.html", "text/html")

        st.markdown("---")
        st.markdown("#### Cover Image Generator")
        if st.button("Generate Cover Image"):
            with st.spinner("Generating..."):
                img_bytes = generate_image_bytes(f"Luxury apartment exterior {b_proj} {b_loc} golden hour")
                if img_bytes:
                    st.image(img_bytes, caption="Generated")
                    st.session_state["_last_cover_bytes"] = img_bytes
                    st.download_button("Download Image", img_bytes, "cover.png", "image/png")
                else:
                    st.warning("Auto-generation not supported. Use Image Studio tab for prompts.")

    # 7. CLOUD UPLOADS (NEW)
    with tabs[6]:
        st.markdown("#### ☁️ Cloud Upload")
        if st.session_state.get("_last_cover_bytes"):
            st.image(st.session_state["_last_cover_bytes"], width=300)
            dest = st.selectbox("Destination", ["AWS S3", "Google Cloud Storage"])
            bucket = st.text_input("Bucket Name")
            if st.button("Upload"):
                if dest == "AWS S3":
                    st.write(upload_s3(st.session_state["_last_cover_bytes"], bucket, f"covers/{int(time.time())}.jpg"))
                else:
                    st.write(upload_gcs(st.session_state["_last_cover_bytes"], bucket, f"covers/{int(time.time())}.jpg"))
        else:
            st.info("Generate an image in the Blog tab first.")

    # 8. ZOHO
    with tabs[7]:
        st.info("Zoho Deluge")
        req = st.text_area("Logic")
        if st.button("Code"): st.code(ask_ai(f"Zoho script: {req}"), language="java")
