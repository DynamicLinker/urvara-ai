import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)
api_key = os.getenv("api_key")

def get_chat_session_file(soil_data, region_info, weather_data, predicted_crops, language="English", file_path=None):
    if not api_key:
        raise ValueError("API Key not found. Please set it in .env file.")
        
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
        if file_path:
            # Read file bytes for inline data
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            mime_type = "application/pdf" if file_path.lower().endswith('.pdf') else "image/png"
            if not file_path.lower().endswith('.pdf') and not file_path.lower().endswith('.png'):
                # Handle other image types if necessary, default to jpeg if not png/pdf
                if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    mime_type = "image/jpeg"

            # Send file and prompt in one single request using inline_data
            response = chat.send_message([
                prompt,
                {
                    "mime_type": mime_type,
                    "data": file_data
                }
            ])
        else:
            response = chat.send_message(prompt)
            
        return chat, response.text
    except Exception as e:
        print(f"Error sending file to Gemini in one go: {e}")
        # Fallback to text-only if multi-modal fails
        try:
            response = chat.send_message(prompt)
            return chat, response.text
        except:
            return None, f"Error: {e}"
