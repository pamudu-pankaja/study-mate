from google import genai
from google.genai import types
from app import GOOGLE_API_KEY


class GeminiLLM():

    def __init__(self , model="gemini-1.5-flash", tools =None):
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
            self.model = self.client.models.get(model)
            self.tools = tools
        
    def get_response(self, query , context = None):
        prompt=query if not context else f"{context}\n\nUser Query : {query}"

        try:
            response = self.model.generete_content(
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config=types.GenerateContentConfig(
                    system_instruction=("\n\nYou are an AI assistant designed to help users learn"
                                         "\n\nand explore topics based on textbooks, academic sources, and external web data."
                                         "\n\n You can provide comprehensive answers by retrieving information from these sources,"
                                         "\n\n but make sure to always prioritize factual and reliable content.Also don't give a too much long answer to the query unless the user asks"
                                         "\n\n If a query requires web scraping, you should inform the user and ensure the data is trustworthy and include the web url."
                                         " \n\nYou are not limited to just textbooks; feel free to answer any educational or general query,"
                                         "\n\n while maintaining a respectful and informative tone. If the user's question is unclear or too broad, ask for clarification to ensure accuracy."
                                         " \n\n If the query contains multiple languages, detect the primary language the user expects a response in. Then answer in that language. You may translate context if needed. "
                                         "\n\nIf u didn't received any extra information, use your general knowledge")
                )
            )
            return response
        except Exception as e:
             return f"LLM Error : {e}"
             