import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
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

class SoilParser:
    def __init__(self):
        if not api_key:
            raise ValueError("API Key not found. Please set 'api_key' in your .env file or Streamlit Secrets.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite')

    def parse_image(self, file_path):
        """
        Parses soil metrics (N, P, K, pH) from an image or PDF file using Gemini Vision.
        Handles various orientations and bilingual (English/Hindi) text.
        Sends file and prompt in one go using inline_data.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            mime_type = "application/pdf" if file_path.lower().endswith('.pdf') else "image/jpeg"
            if file_path.lower().endswith('.png'):
                mime_type = "image/png"

            prompt = """
            Analyze this soil test report. 
            - The report might be a PDF or an image, and it could be in any orientation.
            - The text may be in English, Hindi, or both (bilingual).
            - Look for values related to Nitrogen (N), Phosphorus (P), Potassium (K), and pH.
            - If Nitrogen is marked as 'Low/Medium/High', use 30/60/90 as defaults.
            
            Extract the values and return them in STRICT JSON format:
            {
                "n": number,
                "p": number,
                "k": number,
                "ph": number
            }
            Use numbers only. If a value is missing, use these defaults: {"n": 50, "p": 40, "k": 35, "ph": 7.0}.
            Only return the raw JSON object.
            """

            # Sending file and prompt in one single request
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": mime_type,
                    "data": file_bytes
                }
            ])
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            return {
                "n": float(data.get("n", 50)),
                "p": float(data.get("p", 40)),
                "k": float(data.get("k", 35)),
                "ph": float(data.get("ph", 7.0))
            }
        except Exception as e:
            print(f"Parsing Error: {e}")
            return {"n": 50, "p": 40, "k": 35, "ph": 7.0}
