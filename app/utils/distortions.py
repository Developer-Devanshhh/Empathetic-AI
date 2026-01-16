import re

class DistortionAnalyzer:
    """
    Analyzes text for cognitive distortions using regex patterns.
    Detection is conditional on emotional intensity to avoid false positives.
    """
    
    # Simple regex patterns for common distortions
    PATTERNS = {
        "catastrophizing": [
            r"ruined", r"disaster", r"nightmare", r"never recover", 
            r"end of my life", r"hopeless", r"unbearable"
        ],
        "overgeneralization": [
            r"\balways\b", r"\bnever\b", r"\beveryone\b", r"\bnobody\b", 
            r"nothing ever", r"everything is"
        ],
        "black_and_white": [
            r"\bperfect\b", r"\bfailure\b", r"\bhate\b", r"\bworthless\b", 
            r"\buseless\b", r"total mess"
        ]
    }

    def analyze(self, text: str, emotion_score: float) -> list:
        """
        Returns a list of detected distortions, but ONLY if the emotion_score
        exceeds the threshold (0.4). This prevents factual statements like 
        "I always wake up at 7" from being flagged.
        """
        # 1. Threshold Check
        if emotion_score < 0.4:
            return []
            
        detected = []
        text_lower = text.lower()
        
        # 2. Pattern Matching
        for distortion, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected.append(distortion)
                    break 
                    
        return detected

# Global instance
analyzer = DistortionAnalyzer()
