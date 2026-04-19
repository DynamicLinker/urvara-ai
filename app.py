import streamlit as st
from src.up_data import UP_DISTRICTS
from src.weather import get_weather
from src.advisor import get_recommendation

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

st.markdown("""
    **AI-Powered Agricultural Intelligence** Providing regional crop recommendations and soil health analysis for farmers across UP.
""")
st.divider()

st.sidebar.header("📍 Field Information")
district = st.sidebar.selectbox(
    "Select UP District", 
    options=list(UP_DISTRICTS.keys()),
    index=0
)

st.sidebar.subheader("🧪 Soil Metrics")
p_val = st.sidebar.number_input("Phosphorus (P) Level", min_value=0, max_value=200, value=40)
k_val = st.sidebar.number_input("Potassium (K) Level", min_value=0, max_value=300, value=35)
ph_val = st.sidebar.slider("Soil pH Level", 4.0, 10.0, 7.0, step=0.1)

st.sidebar.info(f"**Target Zone:** {UP_DISTRICTS[district]['zone']}")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Current Environment")
    with st.spinner(f"Getting live weather for {district}..."):
        weather_info = get_weather(district)
    
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

if st.button("🚀 Analyze & Generate Advice"):
    with st.spinner("Generating AI Analysis..."):

        region_info = UP_DISTRICTS[district]
        region_info['district'] = district
        
        soil_data = {
            "p": p_val,
            "k": k_val,
            "ph": ph_val
        }
        
        try:
            advice_report = get_recommendation(soil_data, region_info, weather_info)
            
            st.subheader("📋 Agricultural Advisor Report")
            st.markdown(advice_report)
            
            st.success("Analysis complete. Hope this helps with your harvest!")
            
        except Exception as e:
            st.error(f"Something went wrong with the AI advisor: {e}")
