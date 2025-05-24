from config.config import GOOGLE_API_KEY
from google import genai

client = genai.Client(api_key=GOOGLE_API_KEY)


def translate_to_english(text, target_language="en"):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": f"Translate this text to {target_language}: {text}"}
                    ],
                }
            ],
            config=genai.types.GenerateContentConfig(
                system_instruction="You are a translator. Translate the input text to the specified language.You are only supposed to return the translated text"
            ),
        )
        return response.text.strip()
    except Exception as e:
        return f"Error during translation: {e}"
