import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"Environment Variable 'GEMINI_API_KEY' Found: {bool(key)}")

if not key:
    print("CRITICAL: GEMINI_API_KEY is missing from .env or environment!")
else:
    genai.configure(api_key=key)
    
    print("\n--- Available Generative Models ---")
    try:
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                found = True
        if not found:
            print("No models found supporting 'generateContent'. Check API key permissions.")
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\n--- Testing Generation (gemini-1.5-flash) ---")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Test")
        print("Success! Response:", response.text)
    except Exception as e:
        print(f"Failed with gemini-1.5-flash: {e}")

    print("\n--- Testing Generation (gemini-pro) ---")
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Test")
        print("Success! Response:", response.text)
    except Exception as e:
        print(f"Failed with gemini-pro: {e}")
