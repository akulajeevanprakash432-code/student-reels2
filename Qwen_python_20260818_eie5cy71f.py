import os
import json
from openai import OpenAI

# Initialize OpenAI client (will use OPENAI_API_KEY from environment variables)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))

SYSTEM_PROMPT = """You are an expert content-recommendation strategist for a short-video platform used by engineering students. Your job is NOT to match keywords. Your job is to read a student's recent watch history like a psychologist reads behavior — and find the underlying interest driving it.

Rules:
- Reject lazy keyword matches. Find the CATEGORY of person who watches this sequence.
- Reject hype-bait. Recommend genuinely educational/skill-building content.
- If history < 2 reels, set confidence to Low.
- Output STRICTLY in valid JSON format with these exact keys: 
  "current_reel", "interest_detected", "why", "recommended_tech_reel", "category", "why_this_recommendation", "difficulty", "confidence".
- Do not include markdown formatting like ```json in your response. Just the raw JSON."""

def analyze_watch_history(history_text: str) -> dict:
    """Analyzes the watch history and returns the structured recommendation."""
    
    # Fallback mock if no API key is provided (useful for testing deployment)
    if os.getenv("OPENAI_API_KEY") in [None, "", "mock-key"]:
        return {
            "current_reel": history_text.split("->")[-1].strip("[] "),
            "interest_detected": "Software Engineering Career Preparation (Mock Mode - Add API Key)",
            "why": "This is a mock response. Please add your OPENAI_API_KEY to Render Environment Variables to enable real AI inference.",
            "recommended_tech_reel": "System Design Basics: How to Think About Scalability",
            "category": "HLD",
            "why_this_recommendation": "Mock recommendation to demonstrate UI layout.",
            "difficulty": "Beginner",
            "confidence": "Low"
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Cost-effective and fast
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Watch History: {history_text}"}
            ],
            temperature=0.7,
            response_format={ "type": "json_object" }
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        return {"error": f"AI inference failed: {str(e)}"}