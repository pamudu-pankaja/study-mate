from google import genai
from google.genai import types

class Embedding:

    def get_embedding(self,query):
        
        client = genai.Client(api_key="AIzaSyD7hTDF1Olx5Qg_p9hsZmt3AR8B9xKNZl0")

        query = query.lower()    
        
        try:
            result = client.models.embed_content(
                model = "text-embedding-004",
                contents=f"{query}",
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
            )
            return result.embeddings[0].values
        except Exception as e:
            return f"Error during embedding {e}"

query = "hello"
embedder = Embedding()

result = embedder.get_embedding(query)

print(result)