import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# --- 1. PROFESSIONAL CONFIGURATION ---
st.set_page_config(
    page_title="KonnectOps | Enterprise Edition",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Executive Dashboard" Look
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Professional Button Styling */
        .stButton>button {
            width: 100%;
            background-color: #002D62; /* Home Konnect Blue */
            color: white;
            border-radius: 6px;
            height: 3em;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #004080;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Inputs & Text Areas */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 6px;
            border: 1px solid #d1d5db;
        }
        
        /* Status Container Styling */
        .stStatusWidget {
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR: SYSTEM STATUS ---
with st.sidebar:
    st.markdown("### 🏢 KonnectOps")
    st.caption("Digital Operations Center v6.0")
    
    api_key = st.text_input("🔑 Google API Key", type="password")
    valid_model_name = None

    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Robust Auto-Discovery
            all_models = list(genai.list_models())
            text_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
            
            if text_models:
                # Priority Selection: Flash -> Pro -> First Available
                valid_model_name = text_models[0]
                for m in text_models:
                    if 'flash' in m and 'legacy' not in m:
                        valid_model_name = m
                        break
                st.success(f"🟢 System Online\nModel: `{valid_model_name}`")
            else:
                st.error("🔴 No text models found on this key.")
        except Exception as e:
            st.error(f"🔴 Connection Failed")
    
    st.markdown("---")
    st.markdown("**Active Persona:**\n👨‍💼 Sr. Digital Marketing Exec")

# --- 3. AI CORE FUNCTIONS (Robust Error Handling) ---
def run_ai_task(prompt, task_desc="Processing"):
    """
    Executes an AI task with a professional progress status.
    """
    if not api_key or not valid_model_name:
        st.error("⚠️ System Offline: Please verify API Key.")
        return None

    # Professional "Working" Indicator
    with st.status(f"🤖 {task_desc}...", expanded=True) as status:
        try:
            st.write("🔄 Connecting to Neural Network...")
            model = genai.GenerativeModel(valid_model_name)
            
            st.write("🧠 Analyzing Context & Trends...")
            # Enforce the Persona in every call
            persona_prompt = f"""
            ROLE: Act as a Senior Digital Marketing Executive and Full Stack Developer for 'Home Konnect' (Chennai Real Estate).
            TONE: Professional, Authoritative, Persuasive, and SEO-Optimized.
            TASK: {prompt}
            """
            response = model.generate_content(persona_prompt)
            
            st.write("✨ Polishing Output...")
            time.sleep(0.5) # UX pause for readability
            
            status.update(label="✅ Task Complete", state="complete", expanded=False)
            return response.text
            
        except Exception as e:
            status.update(label="❌ Task Failed", state="error")
            st.error(f"Error details: {e}")
            return None

# --- 4. MAIN APPLICATION ---
st.title("🚀 Home Konnect Digital HQ")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Landing Page Factory", 
    "✍️ Blog & Content", 
    "🎨 Image Studio", 
    "📅 Festival Calendar",
    "👨‍💻 Zoho Helper"
])

# ====== TAB 1: LANDING PAGE FACTORY ======
with tab1:
    st.header("Landing Page Generator")
    c1, c2 = st.columns(2)
    with c1:
        project_name = st.text_input("Project Name", placeholder="e.g. TVS Emerald Luxor")
        location = st.text_input("Location", placeholder="e.g. Anna Nagar")
        price = st.text_input("Price", placeholder="e.g. 1.5 Cr")
    with c2:
        old_name = st.text_input("Template Placeholder", value="Casagrand Flagship")
        html_code = st.text_area("Paste Master HTML Code", height=200)

    if st.button("⚡ Build Page"):
        if html_code:
            # 1. Technical Swap
            final_html = html_code.replace(old_name, project_name)
            final_html = final_html.replace("{PRICE}", price)
            final_html = final_html.replace("{LOCATION}", location)
            
            # 2. AI SEO Injection
            seo_desc = run_ai_task(
                f"Write a high-ranking SEO meta description (155 chars) for {project_name} in {location}. Focus on Luxury & ROI.",
                task_desc="Generating SEO Metadata"
            )
            
            if seo_desc:
                final_html = final_html.replace("{DESC}", seo_desc)
                st.success("Build Successful!")
                st.download_button("⬇️ Download HTML", final_html, f"{project_name}.html", mime="text/html")

# ====== TAB 2: CONTENT STUDIO ======
with tab2:
    st.header("Content Studio")
    content_mode = st.radio("Select Output:", ["📝 SEO Blog Post", "📱 Social Media Carousel", "📧 Client Email"], horizontal=True)
    
    if content_mode == "📝 SEO Blog Post":
        title = st.text_input("Blog Title", placeholder="e.g. Top 5 Investment Hotspots in Chennai 2026")
        if st.button("Draft Article"):
            prompt = f"""
            Write a comprehensive blog post for title: '{title}'.
            Structure:
            1. H1 Title
            2. Catchy Introduction (Hook)
            3. 3-4 Body Paragraphs with H2 Headers
            4. Conclusion + CTA (Call Home Konnect)
            5. Suggest a 'Prompt' for an Image Generator for the Cover Image.
            """
            result = run_ai_task(prompt, task_desc="Drafting Blog Post")
            if result: st.markdown(result)

    elif content_mode == "📱 Social Media Carousel":
        topic = st.text_input("Topic", placeholder="e.g. Why buy in OMR?")
        if st.button("Design Carousel"):
            prompt = f"""
            Create a 5-Slide Instagram Carousel Script for: '{topic}'.
            Format:
            Slide 1: Hook + Image Idea
            Slide 2-4: Value Points
            Slide 5: CTA + Hashtags
            """
            result = run_ai_task(prompt, task_desc="Designing Carousel")
            if result: st.markdown(result)

# ====== TAB 3: IMAGE STUDIO (NEW) ======
with tab3:
    st.header("🎨 AI Image Studio")
    st.info("Generate prompts for Cover Images & Section Visuals.")
    
    img_topic = st.text_input("Describe the Image you need", placeholder="e.g. Luxury apartment living room with sea view in Chennai")
    style = st.selectbox("Art Style", ["Photorealistic", "Minimalist Illustration", "Cinematic Render", "Digital Art"])
    
    if st.button("✨ Generate Image Prompt"):
        prompt = f"""
        Write a highly detailed Text-to-Image Prompt for Midjourney/DALL-E based on: '{img_topic}'.
        Style: {style}.
        Include details on lighting, camera angle, and color palette.
        """
        result = run_ai_task(prompt, task_desc="Engineering Image Prompt")
        if result:
            st.success("Copy this prompt into Midjourney/Canva/Bing Image Creator:")
            st.code(result, language="text")
            st.caption("Note: Direct image generation requires a paid Vertex AI account. This prompt engineer ensures you get the best result on any platform.")

# ====== TAB 4: FESTIVAL CALENDAR ======
with tab4:
    st.header("📅 2026 Marketing Calendar")
    
    # Static Data
    data = {
        "Date": ["Jan 14", "Jan 26", "Mar 04", "Mar 20", "Apr 14", "Aug 15", "Aug 26", "Sep 14", "Oct 20", "Nov 08", "Dec 25"],
        "Festival": ["Pongal", "Republic Day", "Holi", "Ramzan *", "Tamil New Year", "Independence Day", "Onam", "Ganesh Chaturthi", "Ayudha Puja", "Diwali", "Christmas"],
        "Day": ["Wed", "Mon", "Wed", "Fri", "Tue", "Sat", "Wed", "Mon", "Tue", "Sun", "Fri"]
    }
    st.table(pd.DataFrame(data))
    
    target_fest = st.selectbox("Pick a Festival for Campaign", data["Festival"])
    if st.button("Plan Campaign"):
        prompt = f"Create a 3-step Digital Marketing Campaign for '{target_fest}' targeting NRIs for Home Konnect."
        result = run_ai_task(prompt, task_desc="Planning Campaign")
        if result: st.markdown(result)

# ====== TAB 5: ZOHO HELPER ======
with tab5:
    st.header("Zoho Deluge Architect")
    task = st.text_area("Requirement", placeholder="e.g. Auto-assign leads from OMR to Sales Agent 'Rahul'.")
    
    if st.button("Code Script"):
        prompt = f"Write a production-ready Zoho Deluge script for: {task}. Include error handling and comments."
        result = run_ai_task(prompt, task_desc="Compiling Code")
        if result: st.code(result, language='java')
