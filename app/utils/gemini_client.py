import os
import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Use a stable model name
MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

def generate_empathetic_reply(emotion: str, context: str, user_entry: str, distortions: list = None) -> str:
    """Generate a warm, empathetic reflection using Gemini."""
    
    distortion_instruction = ""
    if distortions:
        distortion_list = ", ".join(distortions)
        distortion_instruction = f"""
        OBSERVATION: The user's entry contains these thinking patterns: {distortion_list}.
        INSTRUCTION: Gently invite alternative perspectives using reflective questions. 
        IMPORTANT: Do NOT name or label the distortion explicitly (e.g. do not say "You are catastrophizing"). 
        Instead, ask open questions like "What evidence do you have for that?" or "Is there another way to see this?"
        """

    prompt = f"""
    You are an empathetic journaling companion.
    The user's emotional tone is: {emotion}

    --- Past reflections/context ---
    {context}

    --- New journal entry ---
    {user_entry}
    
    {distortion_instruction}

    Write a supportive reflection that validates the user's feelings,
    encourages gentle introspection, and uses an understanding, positive tone.
    """

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        if hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text.strip()

        return "I'm here to listen — I couldn't generate a full reflection right now."

    except Exception as e:
        print(f"[ERROR] Gemini generation failed: {e}")
        return "I'm here to listen — it seems something went wrong while generating your reflection."
