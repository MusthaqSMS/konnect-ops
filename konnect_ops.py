import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KonnectOps | Smart Edition",
    page_icon="🏢",
    layout="wide"
)

# Professional UI Styling
st.markdown("""
<style>
    .main {background-color: #f4f6f9;}
    .stButton>button {
        width: 100%;
        background-color: #002D62; 
        color: white; 
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .stTextInput>div>div>input {border-radius: 8px;}
    h1, h2, h3 {color: #002D62;}
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR (Setup & Auto-Detect) ---
with st.sidebar:
    # Logo Placeholder
    st.markdown("## 🏢 KonnectOps")
    st.caption("Smart Model Auto-Detect System")
    
    api_key = st.text_input("🔑 Enter Google Gemini API Key", type="password")
    
    # Global variable to store the working model name
    valid_model_name = None

    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # --- SMART AUTO-DETECT LOGIC ---
            with st.spinner("Connecting to Google AI..."):
                # 1. Ask Google: "What models can I use?"
                all_models = list(genai.list_models())
                
                # 2. Filter: Keep only models that can generate text
                text_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
                
                if text_models:
                    # 3. Selection Strategy: Prefer 'flash', otherwise take the first available
                    valid_model_name = text_models[0] # Default to first one found
                    
                    # Try to find a specific 'flash' model if possible
                    for m in text_models:
                        if 'flash' in m and 'legacy' not in m:
                            valid_model_name = m
                            break
                    
                    st.success(f"🟢 Connected! Using: **{valid_model_name}**")
                else:
                    st.error("🔴 Key valid, but no text models found.")
                
        except Exception as e:
            st.error(f"🔴 Connection Error: {e}")
    
    st.markdown("---")
    st.info("v4.5 | Self-Healing Engine")

# --- 3. AI FUNCTION (The Brain) ---
def ask_gemini(prompt):
    if not api_key:
        return "⚠️ Please enter your API Key in the sidebar first."
    if not valid_model_name:
        return "⚠️ No valid model detected. Check your API Key."
    
    try:
        # Use the auto-detected model name
        model = genai.GenerativeModel(valid_model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 4. MAIN DASHBOARD ---
st.title("🚀 Home Konnect Digital HQ")
st.markdown("Your AI-powered real estate operations center.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Landing Page Factory", 
    "✍️ Content Studio", 
    "👨‍💻 Zoho Deluge Helper", 
    "🎉 Event Planner"
])

# ====== TAB 1: LANDING PAGE FACTORY ======
with tab1:
    st.header("Landing Page Generator")
    col1, col2 = st.columns(2)
    with col1:
        new_project = st.text_input("New Project Name", placeholder="e.g. TVS Emerald Luxor")
        new_loc = st.text_input("Location", placeholder="e.g. Porur")
        new_price = st.text_input("Price", placeholder="e.g. 85 Lakhs")
        old_project = st.text_input("Placeholder Name", value="Casagrand Flagship")
    with col2:
        template = st.text_area("Paste Master HTML Code", height=200, help="Paste your source code here.")
        
    if st.button("Generate Landing Page Code"):
        if template:
            # Basic Text Replacement
            final_code = template.replace(old_project, new_project)
            final_code = final_code.replace("{PRICE}", new_price)
            final_code = final_code.replace("{LOCATION}", new_loc)
            
            # AI SEO Injection (Only if AI is ready)
            if api_key and valid_model_name:
                with st.spinner("🤖 AI is writing unique SEO meta-tags..."):
                    seo_prompt = f"Write a 160-character attractive SEO description for a real estate project named {new_project} in {new_loc}. Focus on ROI and Luxury."
                    seo_desc = ask_gemini(seo_prompt)
                    final_code = final_code.replace("{DESC}", seo_desc)
                    st.toast("SEO Metadata Injected Successfully!")
            
            st.success("Code Generated!")
            st.download_button("⬇️ Download HTML File", final_code, f"{new_project.replace(' ','_')}.html", mime="text/html")
        else:
            st.warning("Please paste the HTML template first.")

# ====== TAB 2: CONTENT STUDIO ======
with tab2:
    st.header("Marketing Content Generator")
    col1, col2 = st.columns([1, 3])
    with col1:
        c_type = st.selectbox("Content Type", ["Instagram Carousel", "LinkedIn Post", "Blog Article", "Client Email"])
    with col2:
        topic = st.text_input("Topic / Property Details", placeholder="e.g. Why invest in OMR now? 3BHK, 90L")
    
    if st.button("Draft Content"):
        if api_key:
            with st.spinner("Thinking..."):
                prompt = f"""
                Act as Home Konnect Senior Marketing Manager (Chennai Real Estate).
                Task: Write a {c_type} about {topic}.
                Tone: Professional, Trustworthy, CRISIL-rated.
                Format: Clean text, use emojis if social media.
                """
                result = ask_gemini(prompt)
                st.text_area("Generated Draft:", value=result, height=400)
                st.download_button("Download Text", result, "draft.txt")

# ====== TAB 3: ZOHO DELUGE HELPER ======
with tab3:
    st.header("Zoho Deluge Assistant")
    st.info("Describe the automation you need, and I will write the Deluge code.")
    task = st.text_area("What do you want to automate?", placeholder="e.g. When a Lead Status is updated to 'Closed Won', create an Invoice in Zoho Books.")
    
    if st.button("Write Deluge Script"):
        if api_key:
            with st.spinner("Coding in Deluge..."):
                prompt = f"Write a Zoho Deluge script to: {task}. Add comments explaining each line. Assume standard module names."
                st.code(ask_gemini(prompt), language='java')

# ====== TAB 4: EVENT PLANNER ======
with tab4:
    st.header("Event Brainstorming")
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    with col2:
        audience = st.selectbox("Target Audience", ["NRIs", "Investors", "First Time Buyers"])
        
    if st.button("Generate Event Ideas"):
        if api_key:
            with st.spinner("Brainstorming ideas..."):
                prompt = f"Suggest 3 creative real estate marketing events for {month} in Chennai targeting {audience}. Include event names and activities."
                st.write(ask_gemini(prompt))
