from pinecone import Pinecone, ServerlessSpec
from app.config.config import PINECORN_API_KEY
import time

pc = Pinecone(api_key=PINECORN_API_KEY)


class pinecone_db:
    @staticmethod
    def create_index(index_name):

        try:
            if index_name not in pc.list_indexes():
                pc.create_index(
                    name=index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            return "CREAT INDEX SUCCESSFUL"
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                return "WORKING ON A ALREADY EXISTS INDEX"
            else:
                return f"Error while requasting : {e}"

    @staticmethod
    def upsert(data, namespace,index_name="text-books"):
        from app.agents.rag_agent.vector_store.embedder import Embedding

        try:
            data = [
                d for d in data if isinstance(d, dict) and "text" in d and "id" in d
            ]
            data_texts = [d["text"] for d in data]
            
            print("Embedding the Chunks...")
            embeddings = Embedding.get_embedding_chunks(data_texts)

            if len(embeddings) != len(data):
                return f"Error: Mismatch between data ({len(data)}) and embeddings ({len(embeddings)})"

            vectors = []
            for d, e in zip(data, embeddings):
                if e is not None and isinstance(e, list):
                    if len(e) == 768:
                        vectors.append(
                            {
                                "id": str(d["id"]),
                                "values": e,
                                "metadata": {
                                    "text": d["text"],
                                    "page": str(d.get("page")),
                                    "section": str(d.get("section")),
                                },
                            }
                        )
                else:
                    pass
                    print(f"Invalid embedding for id {d['id']}. Skipping ..")
            else:
                pass
                print(f"Skipping invalid embedding for id {d['id']} (embedding is None or not a list)")

            if vectors:
                pass
            
            if not vectors:
                print(
                    "No valid vectors to upsert (all embeddings may have failed or were invalid)."
                )
                return None

            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

            index = pc.Index(index_name)


            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                res = index.upsert(vectors=batch, namespace=namespace)
                print(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")

            print(f"SUCCESS: {len(vectors)} vectors were added in batches.")
            return "success"

        except Exception as e:
            print(f"Erro while storing : {e}")
            return "error"
