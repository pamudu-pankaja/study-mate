from google import genai
from google.genai import types
from config.config import GOOGLE_API_KEY

class Embedding:
    @staticmethod
    def get_embedding_query(query):
        
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
    
    @staticmethod
    def get_embedding_chunks(data_list):
        
        client = genai.Client(api_key=GOOGLE_API_KEY)
        embeddings = []

        for text in data_list:
            try :
                result = client.models.embed_content(
                    model="text-embedding-004",
                    contents=f"{text}",
                    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
                )
                embeddings.append(result.embeddings[0].values)
                
            except Exception as e:
                return f"Error during embedding : {e}"
        return embeddings