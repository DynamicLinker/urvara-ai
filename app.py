import streamlit as st
from src.up_data import UP_DISTRICTS
from src.weather import get_weather
from src.advisor import get_chat_session
from src.advisorfile import get_chat_session_file
from src.ml_model import predict_crops
from src.upload import SoilParser
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="UP Smart Crop Advisor",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 UrvaraAI")

st.markdown("""
    <style>
    /* 1. General App Background */
    .main { background-color: transparent; }

    /* 2. Style for the Analyze Button */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        height: 3em; 
        background-color: #2e7d32; 
        color: white; 
    }

    /* 3. Theme-Aware Metric Cards */
    
    /* LIGHT THEME: Black Background, White Text */
    @media (prefers-color-scheme: light) {
        div[data-testid="stMetric"] {
            background-color: #1e1e1e !important;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }
    }

    /* DARK THEME: White Background, Black Text */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {
            background-color: #ffffff !important;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
            color: #000000 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

import re

# TTS Helper function
def speak_text(text):
    # 1. Strip Markdown characters (#, *, _, `, etc.)
    # Remove headers (###), bold/italic (**), bullet points (-), and backticks
    clean_text = re.sub(r'[#*_`\-]', ' ', text)
    
    # 2. Normalize whitespace and sanitize for JS string
    clean_text = clean_text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    tts_html = f"""
        <script>
        function speak() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_text}");
            
            function setVoice() {{
                var voices = window.speechSynthesis.getVoices();
                // Priority: 1. Hindi (hi-IN), 2. Indian English (en-IN), 3. Any English
                var isHindi = /[\u0900-\u097F]/.test("{clean_text}");
                var selectedVoice;
                
                if (isHindi) {{
                    selectedVoice = voices.find(v => v.lang.includes('hi'));
                }}
                
                if (!selectedVoice) {{
                    selectedVoice = voices.find(v => v.lang === 'en-IN') || 
                                    voices.find(v => v.lang.startsWith('en-IN')) ||
                                    voices.find(v => v.lang.startsWith('en'));
                }}
                
                if (selectedVoice) {{
                    msg.voice = selectedVoice;
                    msg.lang = selectedVoice.lang;
                }}
                
                msg.rate = 0.9; // Slightly slower for clarity
                window.speechSynthesis.speak(msg);
            }}

            if (window.speechSynthesis.getVoices().length > 0) {{
                setVoice();
            }} else {{
                window.speechSynthesis.onvoiceschanged = setVoice;
            }}
        }}
        speak();
        </script>
    """
    components.html(tts_html, height=0)

# Initialize Soil Parser
parser = SoilParser()

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_inputs" not in st.session_state:
    st.session_state.last_inputs = {}
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = {"n": 50, "p": 40, "k": 35, "ph": 7.0}

# 2. Header Section
st.markdown("""
    **AI-Powered Agricultural Intelligence** Providing regional crop recommendations and soil health analysis for farmers across UP.
""")
st.divider()

# 3. Sidebar Inputs
st.sidebar.header("📍 Field Information")
language = st.sidebar.radio("Preferred Language", options=["English", "Hindi"], index=0, horizontal=True)

district = st.sidebar.selectbox(
    "Select UP District", 
    options=list(UP_DISTRICTS.keys()),
    index=0
)

st.sidebar.subheader("📸 Upload Soil Report")
uploaded_file = st.sidebar.file_uploader("Upload an image or PDF of your soil test", type=['png', 'jpg', 'jpeg', 'pdf'])

if uploaded_file is not None:
    if st.sidebar.button("🚀 Parse & Analyze Soil"):
        with st.spinner("Analyzing soil report & generating advice..."):
            # 1. Save temporary file
            file_ext = uploaded_file.name.split('.')[-1].lower()
            temp_filename = f"temp_soil_report.{file_ext}"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 2. Parse Report
            parsed = parser.parse_image(temp_filename)
            st.session_state.parsed_data = parsed
            
            # 3. Get Weather (using current district)
            weather_info = get_weather(district)
            
            # 4. Run ML Prediction
            predicted_crops = predict_crops(
                parsed['n'], parsed['p'], parsed['k'], 
                weather_info['temp'], 
                weather_info['humidity'], 
                parsed['ph'], 
                weather_info['rainfall']
            )
            
            # 5. Get Gemini Advice
            try:
                soil_data = {
                    "n": parsed['n'],
                    "p": parsed['p'],
                    "k": parsed['k'],
                    "ph": parsed['ph']
                }
                region_info = UP_DISTRICTS[district]
                region_info['district'] = district
                
                chat, advice_report = get_chat_session_file(soil_data, region_info, weather_info, predicted_crops, language, temp_filename)
                st.session_state.chat = chat
                st.session_state.messages = [{"role": "assistant", "content": advice_report}]
                
                # Update last_inputs to prevent the reset on rerun
                st.session_state.last_inputs = {
                    "n": parsed['n'],
                    "p": parsed['p'],
                    "k": parsed['k'],
                    "ph": parsed['ph'],
                    "district": district,
                    "language": language
                }
                
                st.sidebar.success("Analysis complete!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

st.sidebar.subheader("🧪 Soil Metrics")
n_val = st.sidebar.number_input("Nitrogen (N) Level", min_value=0, max_value=1000, value=int(st.session_state.parsed_data['n']))
p_val = st.sidebar.number_input("Phosphorus (P) Level", min_value=0, max_value=1000, value=int(st.session_state.parsed_data['p']))
k_val = st.sidebar.number_input("Potassium (K) Level", min_value=0, max_value=1000, value=int(st.session_state.parsed_data['k']))
ph_val = st.sidebar.slider("Soil pH Level", 4.0, 10.0, float(st.session_state.parsed_data['ph']), step=0.1)

# Check for input changes to reset context
current_inputs = {
    "n": n_val,
    "p": p_val,
    "k": k_val,
    "ph": ph_val,
    "district": district,
    "language": language
}

if current_inputs != st.session_state.last_inputs:
    st.session_state.chat = None
    st.session_state.messages = []
    st.session_state.last_inputs = current_inputs

st.sidebar.info(f"**Target Zone:** {UP_DISTRICTS[district]['zone']}")

# 4. Main Interface Logic
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Current Environment")
    # Fetch Weather Data
    with st.spinner(f"Getting live weather for {district}..."):
        weather_info = get_weather(district)
    
    # Display Weather Metrics
    w_col1, w_col2 = st.columns(2)
    w_col1.metric("Temperature", f"{weather_info['temp']}°C")
    w_col2.metric("Humidity", f"{weather_info['humidity']}%")
    
    if not weather_info['success']:
        st.caption("⚠️ Note: Using regional climate averages (Weather API inactive).")
    else:
        st.caption("✅ Live weather data synced successfully.")

with col2:
    st.subheader("Regional Context")
    st.write(f"**District:** {district}")
    st.write(f"**Soil Type:** {UP_DISTRICTS[district]['soil']}")
    st.write(f"**Commonly Grown:** {UP_DISTRICTS[district]['typical_crops']}")

st.divider()

# 5. Analysis Trigger
if st.button("🚀 Analyze & Generate Advice"):
    with st.spinner("Generating ML Predictions & AI Analysis..."):
        region_info = UP_DISTRICTS[district]
        region_info['district'] = district
        
        soil_data = {
            "n": n_val,
            "p": p_val,
            "k": k_val,
            "ph": ph_val
        }
        
        try:
            # 1. Get ML Prediction first
            with st.status("Predicting best crops using local ML model...", expanded=True) as status:
                predicted_crops = predict_crops(
                    n_val, p_val, k_val, 
                    weather_info['temp'], 
                    weather_info['humidity'], 
                    ph_val, 
                    weather_info['rainfall']
                )
                st.write(f"**Top 3 ML Recommendations:** {', '.join(predicted_crops)}")
                
                # 2. Get Gemini Advice based on ML results
                st.write(f"Generating expert advice in {language} with Gemini AI...")
                chat, advice_report = get_chat_session(soil_data, region_info, weather_info, predicted_crops, language)
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            st.session_state.chat = chat
            st.session_state.messages = [{"role": "assistant", "content": advice_report}]
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# Display conversation history
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "assistant":
        st.subheader("📋 Agricultural Advisor Report" if i == 0 else "💬 Follow-up Response")
        st.markdown(message["content"])
        
        # Add TTS button for each assistant response
        if st.button("🔊 Listen", key=f"tts_{i}"):
            speak_text(message["content"])
    else:
        st.info(f"**Question:** {message['content']}")

# 6. Follow-up "clarify" section
if st.session_state.chat:
    st.divider()
    # Using a form to ensure the input is cleared on submit and prevent loops
    with st.form("follow_up_form", clear_on_submit=True):
        follow_up = st.text_input("Follow-up Question", placeholder="clarify")
        submitted = st.form_submit_button("Ask Gemini")
        
        if submitted and follow_up:
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat.send_message(follow_up)
                    st.session_state.messages.append({"role": "user", "content": follow_up})
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error in follow-up: {e}")
