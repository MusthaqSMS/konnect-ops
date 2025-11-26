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

# Custom CSS for "Role-Based" Styling & Premium Icons
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Global Font */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #1e293b;
        }
        
        /* Premium Gradient Background */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        /* Hide Streamlit Default Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Professional Button Styling */
        .stButton>button {
            width: 100%;
            background-color: #002D62; /* Home Konnect Blue */
            color: white;
            border-radius: 8px;
            height: 3em;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton>button:hover {
            background-color: #004080;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-1px);
        }
        
        /* Inputs & Text Areas - Card Style */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 10px;
            background-color: #ffffff;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #002D62;
            box-shadow: 0 0 0 2px rgba(0, 45, 98, 0.1);
        }
        
        /* Status Container Styling */
        .stStatusWidget {
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            background-color: #ffffff;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
            box-shadow: 2px 0 5px rgba(0,0,0,0.02);
        }
        
        /* Headings & Icons */
        h1, h2, h3 {
            color: #002D62;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .icon-blue { color: #002D62; margin-right: 8px; }
        .icon-pink { color: #d63384; margin-right: 8px; }
        .icon-green { color: #10b981; margin-right: 8px; }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: rgba(255,255,255,0.5);
            padding: 10px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: transparent;
            border-radius: 6px;
            color: #64748b;
            font-weight: 600;
            border: 1px solid transparent;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
            color: #002D62;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR: SYSTEM STATUS ---
with st.sidebar:
    st.markdown("### <i class='fa-solid fa-building icon-blue'></i> KonnectOps", unsafe_allow_html=True)
    st.caption("Digital Operations Center v7.5")
    st.markdown("---")
    
    api_key = st.text_input("🔑 API Key", type="password", help="Google Gemini API Key")
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
                
                # VISIBLE CONNECTION STATUS
                st.markdown(f"""
                <div style='background-color: #ecfdf5; padding: 12px; border-radius: 8px; border: 1px solid #10b981; margin-top: 10px;'>
                    <i class="fa-solid fa-wifi" style='color: #059669;'></i> 
                    <strong style='color: #065f46; margin-left: 5px;'>SYSTEM ONLINE</strong><br>
                    <div style='font-size: 11px; color: #047857; margin-top: 4px; font-family: monospace;'>
                        MODEL: {valid_model_name.split('/')[-1]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error("🔴 No text models found on this key.")
        except Exception as e:
            st.error(f"🔴 Connection Failed")
    else:
        st.info("Waiting for API Key...")
    
    st.markdown("---")
    st.markdown("**Active Persona:**")
    st.markdown("<div style='display: flex; align-items: center;'><i class='fa-solid fa-user-tie icon-blue'></i> <span>Sr. Marketing Exec</span></div>", unsafe_allow_html=True)

# --- 3. AI CORE FUNCTIONS (Robust Error Handling) ---
def run_ai_task(prompt, task_desc="Processing"):
    """
    Executes an AI task with a professional progress status.
    """
    if not api_key or not valid_model_name:
        st.error("⚠️ System Offline: Please verify API Key.")
        return None

    # Professional "Working" Indicator with Custom Icons
    with st.status(f"⚙️ {task_desc}...", expanded=True) as status:
        try:
            st.write("🔄 Handshaking with Neural Network...")
            model = genai.GenerativeModel(valid_model_name)
            
            st.write("🧠 Analyzing Context & Market Trends...")
            # Enforce the Persona in every call
            persona_prompt = f"""
            ROLE: Act as a Senior Digital Marketing Executive and Full Stack Developer for 'Home Konnect' (Chennai Real Estate).
            TONE: Professional, Authoritative, Persuasive, and SEO-Optimized.
            TASK: {prompt}
            """
            response = model.generate_content(persona_prompt)
            
            st.write("✨ Finalizing & Polishing Output...")
            time.sleep(0.5) # UX pause for readability
            
            status.update(label="✅ Task Complete", state="complete", expanded=False)
            return response.text
            
        except Exception as e:
            status.update(label="❌ Task Failed", state="error")
            st.error(f"Error details: {e}")
            return None

# --- 4. MAIN APPLICATION ---
st.markdown("# <i class='fa-solid fa-rocket icon-blue'></i> Home Konnect Digital HQ", unsafe_allow_html=True)

# Tabs with minimal emojis (icons are inside)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dev Console", 
    "Content Studio", 
    "Image Studio", 
    "Calendar",
    "Deluge IDE"
])

# ====== TAB 1: LANDING PAGE FACTORY (Developer Mode) ======
with tab1:
    st.markdown('<h3 class="icon-blue"><i class="fa-solid fa-code"></i> Landing Page Console</h3>', unsafe_allow_html=True)
    st.info("Safe Mode: Replaces content while preserving exact HTML structure.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### <i class='fa-solid fa-bullseye'></i> Target Project", unsafe_allow_html=True)
        project_name = st.text_input("New Project Name", placeholder="e.g. TVS Emerald Luxor")
        location = st.text_input("New Location", placeholder="e.g. Anna Nagar")
        price = st.text_input("New Price", placeholder="e.g. 1.5 Cr")
        
    with c2:
        st.markdown("#### <i class='fa-solid fa-magnifying-glass'></i> Search & Replace", unsafe_allow_html=True)
        old_name = st.text_input("Old Name to Replace", value="Casagrand Flagship")
        old_location = st.text_input("Old Location to Replace", value="Porur")
        old_price = st.text_input("Old Price to Replace", value="85 Lakhs")
        old_about = st.text_area("Old Description (Context)", height=68, help="Paste a paragraph from the old HTML. The AI will rewrite it for the new project.")

    html_code = st.text_area("Source Code (HTML)", height=300, placeholder="<!-- Paste your live HTML code here -->")

    if st.button("⚡ Build & Compile Page"):
        if html_code:
            # 1. Technical Swap (Safe Python String Replacement - Won't break divs)
            final_html = html_code.replace(old_name, project_name)
            if old_price: final_html = final_html.replace(old_price, price)
            if old_location: final_html = final_html.replace(old_location, location)
            
            # 2. Content Alignment (Smart Description Swap)
            if old_about:
                new_about = run_ai_task(
                    f"Write a compelling 3-sentence real estate project description for '{project_name}' located in '{location}'. Price starts at {price}. Tone: Luxury & Investment. Output: Plain text only (no markdown).",
                    task_desc="Aligning Description Content"
                )
                if new_about:
                    final_html = final_html.replace(old_about, new_about)
                    st.toast("Project Description Updated!")

            # 3. AI SEO Injection
            seo_desc = run_ai_task(
                f"Write a high-ranking SEO meta description (155 chars) for {project_name} in {location}. Focus on Luxury & ROI.",
                task_desc="Generating SEO Metadata"
            )
            
            # Try to inject meta tag if placeholder exists
            if "{DESC}" in final_html and seo_desc:
                final_html = final_html.replace("{DESC}", seo_desc)
                st.toast("SEO Metadata Injected!")
            
            st.success("Build Successful! HTML Structure Preserved.")
            st.download_button("⬇️ Download HTML Asset", final_html, f"{project_name}.html", mime="text/html")

# ====== TAB 2: CONTENT STUDIO (Marketing Mode) ======
with tab2:
    st.markdown('<h3 class="icon-blue"><i class="fa-solid fa-pen-nib"></i> Marketing Command Center</h3>', unsafe_allow_html=True)
    content_mode = st.radio("Select Output:", ["📝 SEO Blog Post", "📱 Social Media Carousel", "📧 Client Email"], horizontal=True)
    
    if content_mode == "📝 SEO Blog Post":
        title = st.text_input("Blog Title Strategy", placeholder="e.g. Top 5 Investment Hotspots in Chennai 2026")
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
        topic = st.text_input("Campaign Topic", placeholder="e.g. Why buy in OMR?")
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

    elif content_mode == "📧 Client Email":
        query = st.text_area("Client Query", placeholder="Asking about rental yield...")
        if st.button("Draft Reply"):
            result = run_ai_task(f"Write a professional reply to: {query}", task_desc="Drafting Email")
            if result: st.text_area("Draft", result, height=300)

# ====== TAB 3: IMAGE STUDIO (NEW) ======
with tab3:
    st.markdown('<h3 class="icon-blue"><i class="fa-solid fa-palette"></i> AI Image Studio</h3>', unsafe_allow_html=True)
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
    st.markdown('<h3 class="icon-blue"><i class="fa-regular fa-calendar-check"></i> 2026 Marketing Calendar</h3>', unsafe_allow_html=True)
    
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

# ====== TAB 5: ZOHO HELPER (Programmer Mode) ======
with tab5:
    st.markdown('<h3 class="icon-green"><i class="fa-solid fa-terminal"></i> Deluge Scripting IDE</h3>', unsafe_allow_html=True)
    task = st.text_area("Logic Requirement", placeholder="e.g. Auto-assign leads from OMR to Sales Agent 'Rahul'.")
    
    if st.button("Compile Script"):
        prompt = f"Write a production-ready Zoho Deluge script for: {task}. Include error handling and comments."
        result = run_ai_task(prompt, task_desc="Compiling Code")
        if result: st.code(result, language='java')
