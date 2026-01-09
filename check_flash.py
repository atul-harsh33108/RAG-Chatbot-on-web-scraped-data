import os
import google.generativeai as genai

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def check_flash():
    model_name = 'models/gemini-flash-latest' # Or gemini-2.0-flash
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi")
        print(f"  [SUCCESS] Response: {response.text}")
    except Exception as e:
        print(f"  [ERROR] {e}")

if __name__ == "__main__":
    check_flash()
