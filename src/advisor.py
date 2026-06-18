import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)
api_key = os.getenv("api_key")

def get_recommendation(soil_data, region_info, weather_data, language="English"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    prompt = f"""
    You are an expert Agronomist specializing in Uttar Pradesh, India.
    User Location: {region_info['district']} (Zone: {region_info['zone']}, Soil: {region_info['soil']})
    
    Current Soil Inputs:
    - Nitrogen (N): {soil_data.get('n', 'N/A')}
    - Phosphorus (P): {soil_data['p']}
    - Potassium (K): {soil_data['k']}
    - pH Level: {soil_data['ph']}
    
    Upcoming Weather (5-Day Forecast):
    - Avg Temp: {weather_data['temp']}°C
    - Humidity: {weather_data['humidity']}%
    
    Task:
    1. Suggest the top 2 best crops for this specific scenario.
    2. Assess 'Soil Health' based on N, P, K, and pH for this region.
    3. Give a 1-sentence tip for the farmer to improve yield.
    
    Language Requirement: Respond entirely in {language}.
    Tone: Professional, helpful, and concise. Format with Markdown.
    """
    
    response = model.generate_content(prompt)
    return response.text

def get_chat_session(soil_data, region_info, weather_data, language="English"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    prompt = f"""
    You are an expert Agronomist specializing in Uttar Pradesh, India.
    User Location: {region_info['district']} (Zone: {region_info['zone']}, Soil: {region_info['soil']})
    
    Current Soil Inputs:
    - Nitrogen (N): {soil_data.get('n', 'N/A')}
    - Phosphorus (P): {soil_data['p']}
    - Potassium (K): {soil_data['k']}
    - pH Level: {soil_data['ph']}
    
    Upcoming Weather (5-Day Forecast):
    - Avg Temp: {weather_data['temp']}°C
    - Humidity: {weather_data['humidity']}%
    
    Task:
    1. Suggest the top 2 best crops for this specific scenario.
    2. Assess 'Soil Health' based on N, P, K, and pH for this region.
    3. Give a 1-sentence tip for the farmer to improve yield.
    
    Language Requirement: Respond entirely in {language}.
    Tone: Professional, helpful, and concise. Format with Markdown.
    """
    
    chat = model.start_chat(history=[])
    response = chat.send_message(prompt)
    return chat, response.text
