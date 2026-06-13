from google import genai
from config import Config
import time


def generate_patent_draft(prompt_text: str) -> str:
    if not Config.GEMINI_API_KEY:
        return "Gemini API key is missing. Please add GEMINI_API_KEY in your .env file."

    client = genai.Client(api_key=Config.GEMINI_API_KEY)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_text
            )
            return response.text if getattr(response, "text", None) else "No response generated."
        except Exception as e:
            error_text = str(e)

            if attempt < 2 and ("503" in error_text or "429" in error_text or "overloaded" in error_text.lower()):
                time.sleep(2)
                continue

            return f"Error: {error_text}"

    return "Server is busy. Please try again later."