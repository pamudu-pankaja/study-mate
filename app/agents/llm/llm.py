from google import genai
from google.genai import types
from app.config.config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)

class GeminiLLM():

    @staticmethod 
    def get_response( query , context = None):
        # print(context)
        prompt=query if not context else f"""You are a helpful assistant extracting answers from context for a user's query.

                        Use the provided context (retrieved via a vector search or a web search) to answer the user query and Respond in the user's expected language and translate only if needed.
                        If no context is given, use your own knowledge to answer the question clearly.

                        Follow this exact format for the response:

                        Answer: A short, direct answer to the question. Focus only on what's asked. And do not mention that you have extracted this answer from a context

                        Context:
                        - If context is provided: Copy **directly relevant** sentence(s) from the context and summarize. No extra explanation.  
                        - If no context is provided: Write “No external context was provided, so this answer is based on general knowledge.”

                       
                        URLs:
                        - URLs: If the context includes "Sources : ...", list those URLs. If not, write “Not Specified”.

                       
                        Pages and Sections: Format it exactly like this, using bullet points
                        - Pages:  Only the page numbers that were used to get the answer,
                        - Sections: No extra explanation Just the sextions. Use Only 1-2 sections titles that were used to get the answer. Use the given sections . But if the sections are not given , What might be the section for the given context depending on the examples in giving giving context (e.g."3.2 Engagement in Public Debates","Coal Industry","Industrial Revolution"," Receiving of Independence to Sri Lanka"," Impact on the Society"). 
                        
                        Context:
                        {context} 

                        User Query: {query}
                        """

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config=types.GenerateContentConfig(
                    system_instruction=("You are an AI assistant that helps users learn from textbooks and reliable web sources. When using online information, Keep answers short , concise and aligned with model answers. Match their key terms, phrasing, and structure exactly when available (e.g., 'It failed because...'). Avoid extra background, summaries, or phrases like 'consult the textbook' unless asked. Clearly state the purpose and result in cause-effect questions. If a question is unclear or broad, ask for clarification.")
                )
            )
            return response.candidates[0].content.parts[0].text
        except Exception as e:
             return f"LLM Error : {e}"
             