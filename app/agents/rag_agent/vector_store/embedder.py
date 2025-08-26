import time
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
                model="gemini-embedding-001",
                contents=f"{query}",
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY"
                )
            )
            return result.embeddings[0].values
        except Exception as e:
            return f"Error during embedding : {e}"

    @staticmethod
    def get_embedding_chunks(chunks, batch_size=100):

        embeddings = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            attempt = 0
            while True:
                try:
                    result = client.models.embed_content(
                        model="text-embedding-004",
                        contents=batch,
                        config=types.EmbedContentConfig(
                            task_type="SEMANTIC_SIMILARITY"
                        )
                    )

                    if result and result.embeddings:
                        for embedding in result.embeddings:
                            if embedding and embedding.values:
                                embeddings.append(embedding.values)
                            else:
                                embeddings.append(None)
                        break
                except Exception as e:
                    attempt += 1
                    wait = min(60, 2**attempt)
                    print(
                        f"Error on embedding batch {i//batch_size+1}: {e} | retrying in {wait}s"
                    )
                    time.sleep(wait)
        return embeddings
