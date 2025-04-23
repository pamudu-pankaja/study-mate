from google import genai
from google.genai import types
from app.config.config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)

class Embedding:
    @staticmethod
    def get_embedding_query(query):

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
        
        embeddings = []

        for text in data_list:
            # print(f"Text passed to embedding: {text}")
            try :
                result = client.models.embed_content(
                    model="text-embedding-004",
                    contents=f"{text}",
                    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
                )

                # print(f"Embedding result for text (first 60 characters): {text[:60]}")
                # print(f"Embedding response: {result}")

                if result and result.embeddings and result.embeddings[0].values:
                    embeddings.append(result.embeddings[0].values)

                else:
                    # print(f"Embedding failed for : {text[:60]}")
                    embeddings.append(None)
              
            except Exception as e:
                print(f"Error during embedding: {e}")
                embeddings.append(None)
        return embeddings