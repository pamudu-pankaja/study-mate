from google import genai
from google.genai import types
from app.config import GOOGLE_API_KEY

class Embedding:

    def get_embedding(query):
        
        client = genai.Client(api_key=GOOGLE_API_KEY)

        query = query.lower()    
        
        try:
            result = client.models.embed_content(
                model = "text-embedding-004",
                contents=f"{query}",
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
            )
            return result.embeddings[0].values
        except Exception as e:
            return f"Error during embedding : {e}"


