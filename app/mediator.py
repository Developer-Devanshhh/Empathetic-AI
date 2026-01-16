import os
import google.generativeai as genai

# Reuse existing config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"

async def summarize_room(conversation_history: list) -> str:
    """
    Synthesize the conversation into a gentle, non-authoritative summary.
    Input: List of dicts {sender, text}
    Output: String summary
    """
    if not conversation_history:
        return ""

    # Format history
    history_text = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in conversation_history])

    prompt = f"""
    ROLE: You are a gentle, neutral mediator.
    TASK: Offer a brief synthesis of the perspectives shared in the conversation below. 
    CONSTRAINT: Do NOT draw a final conclusion. Do NOT say who is right. 
    Instead, phrase it as "Some perspectives to consider..." or "You might reflect on..."
    Keep it optional and supportive.

    CONVERSATION:
    {history_text}
    
    Synthesis:
    """

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(prompt)
        return response.text.strip() if response.text else ""
    except Exception as e:
        print(f"[Mediator] Failed: {e}")
        return ""
