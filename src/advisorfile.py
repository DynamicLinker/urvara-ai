import os
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image

load_dotenv(override=True)
api_key = os.getenv("api_key")

def get_chat_session_file(soil_data, region_info, weather_data, predicted_crops, language="English", file_path=None):
    genai.configure(api_key=api_key)
    # Using gemini-2.0-flash-exp for robust vision and document support
    model = genai.GenerativeModel('gemini-3.1-flash-lite')

    crops_list = ", ".join(predicted_crops)

    prompt = f"""
    You are an expert Agronomist specializing in Uttar Pradesh, India.
    User Location: provided already.

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
            if file_path.lower().endswith('.pdf'):
                # Upload PDF for Gemini to process
                uploaded_file = genai.upload_file(path=file_path, mime_type="application/pdf")
                response = chat.send_message([prompt, uploaded_file])
            else:
                # Load Image for Gemini to process
                img = PIL.Image.open(file_path)
                response = chat.send_message([prompt, img])
        else:
            response = chat.send_message(prompt)
            
        return chat, response.text
    except Exception as e:
        # Fallback to text-only if file handling fails
        print(f"Error sending file to Gemini: {e}")
        response = chat.send_message(prompt)
        return chat, response.text
