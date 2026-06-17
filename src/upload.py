import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv(override=True)
api_key = os.getenv("api_key")

class SoilParser:
    def __init__(self):
        if not api_key:
            raise ValueError("API Key not found. Please set it in .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite')

    def parse_image(self, file_path):
        """
        Parses soil metrics (N, P, K, pH) from an image or PDF file using Gemini Vision.
        Handles various orientations and bilingual (English/Hindi) text.
        Sends file and prompt in one go using inline_data.
        """
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            mime_type = "application/pdf" if file_path.lower().endswith('.pdf') else "image/png"
            if not file_path.lower().endswith('.pdf') and not file_path.lower().endswith('.png'):
                if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    mime_type = "image/jpeg"

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
                    "data": file_data
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
            print(f"Error parsing soil report in one go: {e}")
            return {"n": 50, "p": 40, "k": 35, "ph": 7.0}
