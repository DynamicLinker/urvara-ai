import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)
api_key = os.getenv("api_key")

def get_chat_session(soil_data, region_info, weather_data, predicted_crops, language="English"):
    genai.configure(api_key=api_key)
    # Using the model version requested by the user
    model = genai.GenerativeModel('gemini-3.1-flash-lite')

    crops_list = ", ".join(predicted_crops)

    prompt = f"""
    You are an expert Agronomist specializing in Uttar Pradesh, India.
    User Location: {region_info['district']} (Zone: {region_info['zone']}, Soil: {region_info['soil']})

    Current Soil Inputs:
    - Nitrogen (N): {soil_data['n']}
    - Phosphorus (P): {soil_data['p']}
    - Potassium (K): {soil_data['k']}
    - pH Level: {soil_data['ph']}

    Current Weather:
    - Temp: {weather_data['temp']}°C
    - Humidity: {weather_data['humidity']}%
    - Rainfall: {weather_data['rainfall']} mm

    Predicted Best Crops (from ML model): {crops_list}

    Task:
    1. Briefly explain why these crops ({crops_list}) are suitable.
    2. Assess 'Soil Health' based on N, P, K, and pH for this region.
    3. Provide a 1-sentence tip for the farmer to improve yield.

    IMPORTANT: Provide the entire response ONLY in {language}. If the language is Hindi, ensure the tone is respectful and uses common agricultural terms used in Uttar Pradesh.

    Tone: Professional, helpful, and concise. Format with Markdown.
    """

    chat = model.start_chat(history=[])
    response = chat.send_message(prompt)
    return chat, response.text

def get_recommendation(soil_data, region_info, weather_data, predicted_crops, language="English"):
    # Backward compatibility or simple call
    chat, text = get_chat_session(soil_data, region_info, weather_data, predicted_crops, language)
    return text