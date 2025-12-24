import streamlit as st
import pandas as pd
import speech_recognition as sr
import webbrowser

# --- 1. CONFIGURATION & CUSTOM CSS ---
st.set_page_config(page_title="JanSeva AI", page_icon="🏛️", layout="wide")

# Custom CSS: STRICT COLOR ENFORCEMENT
st.markdown("""
    <style>
    /* --- GLOBAL SETTINGS --- */
    /* Force entire app background to White */
    .stApp {
        background-color: #ffffff !important;
    }
    /* Force all base text to Black */
    p, h1, h2, h3, h4, h5, h6, span, div, label, li {
        color: #000000 !important;
    }

    /* --- BLUE ELEMENTS (Text must be WHITE) --- */
    
    /* 1. Main Header */
    .main-header {
        background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Force text INSIDE the header to be White */
    .main-header h1, .main-header p {
        color: #ffffff !important;
    }

    /* 2. Buttons (The Blue Buttons) */
    div.stButton > button {
        background-color: #1a237e !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
    }
    /* Force Text inside Buttons to be WHITE */
    div.stButton > button p {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    div.stButton > button:hover {
        background-color: #283593 !important;
        color: #ffffff !important;
    }
    /* Fix for the 'Speak' button specific styling issues */
    div.stButton > button:active {
        color: #ffffff !important;
        background-color: #1a237e !important;
    }

    /* --- WHITE ELEMENTS (Text must be BLACK) --- */

    /* 1. Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    /* Force all Sidebar text to Black */
    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* 2. Input Box (Search Bar) */
    /* Force background White and Text Black */
    .stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }
    /* Force Placeholder text (e.g. "Describe your need...") to Grey */
    .stTextInput input::placeholder {
        color: #666666 !important;
    }

    /* 3. Cards (Results) */
    .scheme-card {
        background-color: #ffffff !important;
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #ff9800;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    /* Force Text inside Cards to Black */
    .scheme-card div, .scheme-card p, .scheme-card span {
        color: #000000 !important;
    }
    /* Exception: The card title should be Blue */
    .card-title {
        color: #1a237e !important;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- TRANSLATIONS ---
translations = {
    "English": {
        "header_title": "🏛️ JanSeva AI",
        "header_subtitle": "Bridging Citizens with Government Benefits",
        "sidebar_title": "👤 User Profile",
        "sidebar_desc": "Configure your profile to find relevant schemes.",
        "select_lang": "Language",
        "select_category": "I am a:",
        "search_label": "🔍 Describe your need (e.g., 'I need a loan for farming')",
        "search_btn": "Find Schemes",
        "voice_btn": "🎤 Speak",
        "voice_listening": "🎧 Listening...",
        "voice_success": "✅ Heard:",
        "voice_error": "❌ Could not understand audio.",
        "whatsapp_btn": "💬 Chat Support",
        "result_found": "Found {} matching schemes",
        "no_result": "No schemes found. Try keywords like 'Loan', 'Study', 'Farm'.",
        "apply_btn": "👉 Apply Now",
        "desc": "Description",
        "who": "Eligibility",
        "benefit": "Benefits",
        "cats": ["All", "Agriculture", "Student", "Business", "Women", "Health", "Housing"]
    },
    "Hindi": {
        "header_title": "🏛️ जनसेवा AI",
        "header_subtitle": "नागरिकों को सरकारी लाभों से जोड़ना",
        "sidebar_title": "👤 उपयोगकर्ता प्रोफाइल",
        "sidebar_desc": "योजनाएं खोजने के लिए अपनी जानकारी दें।",
        "select_lang": "भाषा",
        "select_category": "मैं हूँ एक:",
        "search_label": "🔍 अपनी आवश्यकता बताएं (उदाहरण: 'मुझे खेती के लिए लोन चाहिए')",
        "search_btn": "योजनाएं खोजें",
        "voice_btn": "🎤 बोलें",
        "voice_listening": "🎧 सुन रहा हूँ...",
        "voice_success": "✅ सुना:",
        "voice_error": "❌ स्पष्ट नहीं है।",
        "whatsapp_btn": "💬 सहायता चैट",
        "result_found": "{} योजनाएं मिलीं",
        "no_result": "कोई योजना नहीं मिली। 'लोन', 'पढ़ाई' जैसे शब्द आज़माएं।",
        "apply_btn": "👉 आवेदन करें",
        "desc": "विवरण",
        "who": "पात्रता",
        "benefit": "लाभ",
        "cats": ["All", "Agriculture", "Student", "Business", "Women", "Health", "Housing"]
    }
}

# --- 2. LOAD DATA ---
def load_data():
    try:
        df = pd.read_csv("schemes.csv")
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        return None

# --- 3. VOICE FUNCTION ---
def recognize_speech(language):
    r = sr.Recognizer()
    try:
        # This will fail on Streamlit Cloud (No Hardware)
        with sr.Microphone() as source:
            placeholder = st.empty()
            placeholder.info("🎧 Listening... Speak now!")
            
            # Adjust for ambient noise helps if mic is noisy
            r.adjust_for_ambient_noise(source, duration=0.5)
            
            audio = r.listen(source, timeout=3, phrase_time_limit=3)
            text = r.recognize_google(audio)
            placeholder.empty()
            return text
            
    except OSError:
        # This catches the "No Default Input Device" error on the Cloud
        return "ERROR: NO_MIC"
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except:
        return None

# --- 4. SEARCH LOGIC ---
def find_scheme(category, query, df):
    if category != "All":
        df = df[df['Category'] == category]
    
    if query:
        query = query.lower()
        keywords = query.split()
        results = []
        ignored_words = ['i', 'am', 'need', 'want', 'to', 'how', 'can', 'get', 'a', 'the', 'is', 'for', 'me', 'mai', 'chahiye', 'hai', 'mujhe', 'kya', 'milega']
        
        for index, row in df.iterrows():
            content = str(row['Scheme_Name']) + " " + str(row['Description']) + " " + str(row['Who_Can_Apply']) + " " + str(row['Benefits'])
            content = content.lower()
            score = 0
            for word in keywords:
                if word not in ignored_words and word in content:
                    score += 1
            if score > 0:
                results.append(row)
        return results
    else:
        return [row for index, row in df.iterrows()]

# --- 5. MAIN APP UI ---
def main():
    if 'voice_query' not in st.session_state:
        st.session_state.voice_query = ""

    df = load_data()
    if df is None:
        st.error("❌ Critical Error: 'schemes.csv' file missing. Please create it.")
        return

    # --- SIDEBAR ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2393/2393305.png", width=80)
    lang = st.sidebar.radio("🌐 Language / भाषा", ["English", "Hindi"])
    t = translations[lang]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader(t["sidebar_title"])
    st.sidebar.info(t["sidebar_desc"])
    
    category = st.sidebar.radio(t["select_category"], t["cats"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button(t["whatsapp_btn"]):
        webbrowser.open("https://wa.me/910000000000")
        st.sidebar.success("Opening WhatsApp...")

    # --- MAIN CONTENT ---
    
    # 1. Custom Header (HTML)
    st.markdown(f"""
        <div class="main-header">
            <h1>{t['header_title']}</h1>
            <p>{t['header_subtitle']}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Search & Voice Interface
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Search Box
        user_query = st.text_input(label=t["search_label"], value=st.session_state.voice_query)
    
    with col2:
        st.write("") 
        st.write("")
        with st.container():
            if st.button(t["voice_btn"]):
                voice_text = recognize_speech(lang)
                
                if voice_text == "ERROR: NO_MIC":
                    # Show a friendly warning instead of crashing
                    st.warning("⚠️ Voice unavailable on Cloud Demo. Please run locally for voice features.")
                elif voice_text:
                    st.session_state.voice_query = voice_text
                    st.rerun() 
                else:
                    st.toast(t["voice_error"])
    # 3. Results Area
    if st.button(t["search_btn"], use_container_width=True):
        matches = find_scheme(category, user_query, df)
        
        st.markdown("---")
        if matches:
            st.success(t["result_found"].format(len(matches)))
            
            for scheme in matches:
                clean_link = str(scheme['Link']).replace('"', '').replace("'", "").strip()
                
                # HTML Card
                st.markdown(f"""
                <div class="scheme-card">
                    <div class="card-title">📜 {scheme['Scheme_Name']}</div>
                    <p><span class="card-label">{t['desc']}:</span> {scheme['Description']}</p>
                    <p><span class="card-label">{t['who']}:</span> {scheme['Who_Can_Apply']}</p>
                    <p><span class="card-label">{t['benefit']}:</span> {scheme['Benefits']}</p>
                    <a href="{clean_link}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #4CAF50; color: white !important; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-family: sans-serif;">
                           {t['apply_btn']} 🚀
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(t["no_result"])

if __name__ == "__main__":
    main()
