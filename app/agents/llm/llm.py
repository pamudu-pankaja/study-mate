from google import genai
from google.genai import types
from config.config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)

class GeminiLLM():

    @staticmethod 
    def get_response( query , context = None):
        prompt=query if not context else f"{context}\n\nUser Query : {query}"

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config=types.GenerateContentConfig(
                    system_instruction=("You are an AI assistant that helps users learn from textbooks and reliable web sources. When using online information, include up to three trustworthy URLs. Keep answers concise and aligned with model answers. Match their key terms, phrasing, and structure exactly when available (e.g., 'It failed because...'). Avoid extra background, summaries, or phrases like 'consult the textbook' unless asked. Clearly state the purpose and result in cause-effect questions. If a question is unclear or broad, ask for clarification. Respond in the user's expected language and translate only if needed")
                )
            )
            return response.candidates[0].content.parts[0].text
        except Exception as e:
             return f"LLM Error : {e}"
             