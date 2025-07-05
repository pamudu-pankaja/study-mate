from concurrent.futures import ThreadPoolExecutor, as_completed
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
                model="text-embedding-004",
                contents=f"{query}",
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
            )
            return result.embeddings[0].values
        except Exception as e:
            return f"Error during embedding : {e}"

    @staticmethod
    def get_embedding_chunks(chunks,max_workers=20):
        def embed_single(text):
            try:
                result = client.models.embed_content(
                    model="text-embedding-005",
                    contents=text,
                    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
                )
                return result.embeddings[0].values if result and result.embeddings else None
            except Exception as e:
                print(f"Embedding error: {e}")
                return None

        def get_embedding_chunks_parallel(texts):
            embeddings = [None] * len(texts)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(embed_single, text): idx for idx, text in enumerate(texts)}
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        embeddings[idx] = future.result()
                    except Exception as e:
                        print(f"Embedding error at index {idx}: {e}")
                        embeddings[idx] = None
            return embeddings

        texts = [chunk["text"] for chunk in chunks]
        return get_embedding_chunks_parallel(texts)

