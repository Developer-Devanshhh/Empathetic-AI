import re

# Comprehensive list of crisis keywords (MVP version)
CRISIS_KEYWORDS = [
    r"\bsuicid", r"\bkill myself", r"\bwant to die", r"\bend it all",
    r"\bhurt myself", r"\bself-harm", r"\bcutting myself", r"\boverdose",
    r"\bbetter off dead", r"\bno reason to live", r"\bhopeless",
    r"\bgive up on life", r"\bcan't go on"
]

CRISIS_MESSAGE = """
I hear that you are going through a very difficult time. Please know that you are not alone and there is support available.

If you are in immediate danger or need urgent help, please contact emergency services or a crisis helpline:
- **National Suicide Prevention Lifeline (US):** 988
- **Crisis Text Line:** Text HOME to 741741
- **International:** Please search for "suicide helpline" in your country.

I am an AI and cannot provide professional help, but I encourage you to reach out to a human who can safely support you.
"""

def check_safety(text: str) -> dict:
    """
    Checks text for safety risks using regex patterns.
    
    Returns:
        dict: {
            "is_safe": bool,
            "category": str or None,
            "response_message": str or None
        }
    """
    text_lower = text.lower()
    
    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, text_lower):
            return {
                "is_safe": False,
                "category": "self_harm_crisis",
                "response_message": CRISIS_MESSAGE
            }
            
    return {
        "is_safe": True,
        "category": None,
        "response_message": None
    }
