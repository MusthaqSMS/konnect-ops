import streamlit as st
import google.generativeai as genai
import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KonnectOps | Free Edition",
    page_icon="🏢",
    layout="wide"
)

# Professional UI Styles
st.markdown("""
<style>
    .main {background-color: #f0f2f6;}
    .stButton>button {width: 100%; background-color: #002D62; color: white;}
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🏢 KonnectOps")
    st.caption("Zero-Cost Internal Tool")
    
    # API Key Input
    api_key = st.text_input("🔑 Enter Google Gemini API Key", type="password")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.success("Gemini AI Connected 🟢")
        except:
            st.error("Invalid Key 🔴")
    
    st.markdown("---")
    st.info("Get a free key at aistudio.google.com")

# --- 3. AI FUNCTION (The Brain) ---
def ask_gemini(prompt):
    if not api_key:
        return "⚠️ Please enter your API Key in the sidebar first."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Free, fast model
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 4. DASHBOARD ---
st.title("🚀 Home Konnect Digital HQ")
tab1, tab2, tab3, tab4 = st.tabs(["📄 Landing Page", "✍️ Content Studio", "👨‍💻 Zoho Helper", "🎉 Event Planner"])

# ====== TAB 1: LANDING PAGE ======
with tab1:
    st.header("Landing Page Factory")
    col1, col2 = st.columns(2)
    with col1:
        new_project = st.text_input("New Project Name", placeholder="TVS Emerald")
        new_loc = st.text_input("Location", placeholder="Porur")
        new_price = st.text_input("Price", placeholder="85 Lakhs")
        old_project = st.text_input("Template Placeholder", value="Casagrand Flagship")
    with col2:
        template = st.text_area("Paste HTML Code", height=200)
        
    if st.button("Generate Code"):
        final_code = template.replace(old_project, new_project).replace("{PRICE}", new_price).replace("{LOCATION}", new_loc)
        
        if api_key:
            seo_desc = ask_gemini(f"Write a 160-char SEO description for {new_project} in {new_loc} focusing on ROI.")
            final_code = final_code.replace("{DESC}", seo_desc)
            st.toast("SEO Generated!")
            
        st.download_button("⬇️ Download HTML", final_code, f"{new_project}.html")

# ====== TAB 2: CONTENT STUDIO ======
with tab2:
    st.header("Marketing Content Generator")
    c_type = st.selectbox("Type", ["Instagram Carousel", "LinkedIn Post", "Blog Article"])
    topic = st.text_input("Topic", placeholder="e.g. Why invest in OMR?")
    
    if st.button("Draft Content"):
        prompt = f"Act as Home Konnect Marketing Manager. Write a {c_type} about {topic}. Professional tone."
        st.write(ask_gemini(prompt))

# ====== TAB 3: ZOHO HELPER ======
with tab3:
    st.header("Zoho Deluge Assistant")
    task = st.text_area("What do you want to automate?", placeholder="Update lead status to 'Contacted' when email opens.")
    if st.button("Write Script"):
        prompt = f"Write a Zoho Deluge script to: {task}. Add comments."
        st.code(ask_gemini(prompt), language='java')

# ====== TAB 4: EVENT PLANNER ======
with tab4:
    st.header("Event Brainstorming")
    month = st.selectbox("Month", ["January", "October (Diwali)", "December (Music Season)"])
    if st.button("Get Ideas"):
        prompt = f"Suggest 3 creative real estate marketing events for {month} in Chennai targeting NRIs."
        st.write(ask_gemini(prompt))
