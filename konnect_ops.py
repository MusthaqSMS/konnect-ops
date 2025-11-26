import streamlit as st
import google.generativeai as genai
import datetime
import pandas as pd

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Home Konnect HQ",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Look
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stButton>button {
            width: 100%;
            background-color: #002D62;
            color: white;
            border-radius: 8px;
            height: 3em;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover {
            background-color: #004080;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🏢 KonnectOps")
    st.caption("Digital Operations Center")
    
    api_key = st.text_input("🔑 Google API Key", type="password")
    valid_model_name = None

    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Smart Auto-Detect Logic
            all_models = list(genai.list_models())
            text_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
            
            if text_models:
                valid_model_name = text_models[0]
                for m in text_models:
                    if 'flash' in m and 'legacy' not in m:
                        valid_model_name = m
                        break
                st.success(f"🟢 Connected! ({valid_model_name})")
            else:
                st.error("🔴 No text models found.")
        except Exception as e:
            st.error(f"🔴 Error: {e}")
    
    st.markdown("---")
    st.info("v5.0 | 2026 Ready")

# --- 3. AI LOGIC ---
def ask_gemini(prompt):
    if not api_key or not valid_model_name:
        return "⚠️ API Key missing or invalid."
    try:
        model = genai.GenerativeModel(valid_model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 4. MAIN DASHBOARD ---
st.title("🚀 Home Konnect Digital HQ")

tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Landing Page Factory", 
    "✍️ Content Studio", 
    "📅 Festival Calendar 2026",
    "👨‍💻 Zoho Helper"
])

# ====== MODULE 1: LANDING PAGES ======
with tab1:
    st.header("Landing Page Generator")
    c1, c2 = st.columns(2)
    with c1:
        project_name = st.text_input("New Project Name", placeholder="e.g. TVS Emerald Luxor")
        location = st.text_input("Location", placeholder="e.g. Porur")
        price = st.text_input("Price", placeholder="e.g. 85 Lakhs")
    with c2:
        old_name = st.text_input("Placeholder to Replace", value="Casagrand Flagship")
        html_code = st.text_area("Paste Master HTML Code", height=200)

    if st.button("Generate Page Code"):
        if html_code:
            final_html = html_code.replace(old_name, project_name)
            final_html = final_html.replace("{PRICE}", price)
            final_html = final_html.replace("{LOCATION}", location)
            
            if api_key and valid_model_name:
                seo = ask_gemini(f"Write a 150-char SEO description for {project_name} in {location}.")
                final_html = final_html.replace("{DESC}", seo)
                st.toast("SEO Added!")
            
            st.download_button("⬇️ Download HTML", final_html, f"{project_name}.html", mime="text/html")

# ====== MODULE 2: CONTENT STUDIO (Updated) ======
with tab2:
    st.header("Content Studio")
    
    mode = st.radio("Select Mode:", ["📝 Blog Post (From Title)", "📱 Social Media Post", "📧 Client Email"], horizontal=True)
    
    if mode == "📝 Blog Post (From Title)":
        blog_title = st.text_input("Enter Blog Title", placeholder="e.g. Why OMR is the best investment for NRIs in 2026")
        if st.button("Write Full Blog Post"):
            if api_key:
                with st.spinner("Writing article..."):
                    prompt = f"""
                    Act as a Senior Real Estate Content Writer for Home Konnect.
                    Write a full blog post based on this title: "{blog_title}".
                    
                    Structure:
                    1. Catchy Introduction
                    2. 3-4 Key Points with Data/Trends
                    3. Conclusion with Call to Action (Contact Home Konnect).
                    
                    Tone: Professional, Authoritative, SEO-friendly.
                    """
                    result = ask_gemini(prompt)
                    st.markdown(result)
                    st.download_button("Download Blog", result, "blog_post.txt")
            else:
                st.error("Please enter API Key.")

    elif mode == "📱 Social Media Post":
        topic = st.text_input("Topic", placeholder="e.g. New Launch in Anna Nagar")
        platform = st.selectbox("Platform", ["Instagram Carousel", "LinkedIn Article", "Facebook Post"])
        if st.button("Draft Social Post"):
            if api_key:
                result = ask_gemini(f"Write a {platform} about {topic}. Include emojis and hashtags.")
                st.text_area("Draft:", value=result, height=300)

    elif mode == "📧 Client Email":
        query = st.text_area("Client Query", placeholder="Client asking about property management fees...")
        if st.button("Draft Reply"):
            if api_key:
                result = ask_gemini(f"Write a polite professional email reply to: {query}")
                st.text_area("Draft:", value=result, height=300)

# ====== MODULE 3: FESTIVAL CALENDAR (New) ======
with tab3:
    st.header("📅 Upcoming Indian Festivals (2026)")
    st.caption("Plan your marketing campaigns ahead of time.")
    
    # Static Data for 2026 (Major Festivals)
    data = {
        "Date": [
            "Jan 14, 2026", "Jan 26, 2026", "Mar 04, 2026", 
            "Mar 20, 2026", "Apr 14, 2026", "Aug 15, 2026", 
            "Aug 26, 2026", "Sep 14, 2026", "Oct 20, 2026", 
            "Nov 08, 2026", "Dec 25, 2026"
        ],
        "Festival": [
            "Pongal / Makar Sankranti", "Republic Day", "Holi", 
            "Ramzan (Eid-ul-Fitr) *", "Tamil New Year", "Independence Day", 
            "Onam", "Ganesh Chaturthi", "Ayudha Puja / Dussehra", 
            "Diwali (Deepavali)", "Christmas"
        ],
        "Day": [
            "Wednesday", "Monday", "Wednesday", 
            "Friday", "Tuesday", "Saturday", 
            "Wednesday", "Monday", "Tuesday", 
            "Sunday", "Friday"
        ]
    }
    
    df = pd.DataFrame(data)
    st.table(df)
    st.caption("* Dates for Islamic festivals are subject to moon sighting.")
    
    st.markdown("### 💡 Need a Campaign Idea?")
    selected_fest = st.selectbox("Select Festival", df["Festival"])
    if st.button("Generate Campaign Idea"):
        if api_key:
            idea = ask_gemini(f"Suggest a creative real estate marketing campaign for '{selected_fest}' targeting Home Buyers in Chennai.")
            st.write(idea)

# ====== MODULE 4: ZOHO HELPER ======
with tab4:
    st.header("Zoho Automation Assistant")
    task = st.text_area("Describe automation task", placeholder="e.g. Send email when lead status is 'Hot'")
    if st.button("Generate Script"):
        if api_key:
            st.code(ask_gemini(f"Write Zoho Deluge script for: {task}"), language='java')
