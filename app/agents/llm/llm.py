from google import genai
from google.genai import types
from config.config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)

class GeminiLLM():

    @staticmethod 
    def get_response( query , context = None):
        prompt=query if not context else f"""You are a helpful assistant extracting answers from historical documents.

                        Use the provided context (retrieved via vector search) to answer the user query. Follow this exact format:

                        Answer: A short, direct answer to the question. Focus only on what's asked.

                        Context: Copy **directly relevant** sentence(s) from the context provided. No extra explanation or paraphrasing.

                        Pages and Sections: Format it exactly like this, using bullet points
                        - Pages: Use page numbers if given, else guess logically based on context (e.g., "Page 44",)
                        - Sections: Use the section title from the text if visible (e.g. "Fig  8.12 – British fighter aircraft","3.2 Engagement in Public Debates")

                        Context:
                        {context}

                        User Query: {query}
                        """
        print(context)

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
             