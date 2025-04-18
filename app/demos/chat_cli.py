from google import genai
from google.genai import types
from config import GOOGLE_API_KEY

# Replace with your actual Google API key

@staticmethod
def check_embedding_dimensions(data_list):
    client = genai.Client(api_key=GOOGLE_API_KEY)

    for i, text in enumerate(data_list):
        try:
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=f"{text}",
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
            )
            embedding = result.embeddings[0].values
            print(f"[{i}] Embedding dimension: {len(embedding)}")
            
        except Exception as e:
            print(f"[{i}] Error during embedding: {e}")

# Example usage
data_list = [
    "Your first example text.",
    "Second example of text to check.",
]

check_embedding_dimensions(data_list)
