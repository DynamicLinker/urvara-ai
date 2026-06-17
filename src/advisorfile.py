import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

# Load from .env locally
load_dotenv(override=True)

# Safe lookup for Streamlit Cloud and Local
api_key = os.getenv("api_key")
if not api_key:
    try:
        api_key = st.secrets.get("api_key")
    except:
        pass

def get_chat_session_file(soil_data, region_info, weather_data, predicted_crops, language="English", file_path=None):
    if not api_key:
        raise ValueError("API Key not found. Please set 'api_key' in your .env file or Streamlit Secrets.")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.1-flash-lite')

    crops_list = ", ".join(predicted_crops)

    prompt = f"""
    You are an expert Agronomist specializing in Uttar Pradesh, India.
    User Location: provided in file.

    Task:
    1. Briefly explain why these crops ({crops_list}) are suitable.
    2. Assess 'Soil Health' based on N, P, K, and pH for this region.
    3. Provide a 1-sentence tip for the farmer to improve yield.

    IMPORTANT: Provide the entire response ONLY in {language}. If the language is Hindi, ensure the tone is respectful and uses common agricultural terms used in Uttar Pradesh.

    Tone: Professional, helpful, and concise. Format with Markdown.
    """

    chat = model.start_chat(history=[])
    
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            mime_type = "application/pdf" if file_path.lower().endswith('.pdf') else "image/jpeg"
            if file_path.lower().endswith('.png'):
                mime_type = "image/png"

            # One-go upload using inline_data
            response = chat.send_message([
                prompt,
                {
                    "mime_type": mime_type,
                    "data": file_bytes
                }
            ])
        else:
            response = chat.send_message(prompt)
            
        return chat, response.text
    except Exception as e:
        print(f"Advisory File Error: {e}")
        # Fallback to text-only
        response = chat.send_message(prompt)
        return chat, response.text
