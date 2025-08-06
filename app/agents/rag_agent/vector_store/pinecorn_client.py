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

    def upsert(data, namespace , index_name="text-books"):

        from app.agents.rag_agent.vector_store.embedder import Embedding

        try:
            data = [
                d for d in data if isinstance(d, dict) and "text" in d and "id" in d
            ]
            data_texts = [d["text"] for d in data]

            embeddings = Embedding.get_embedding_chunks(data_texts)

            # print(f"Embeddings length: {len(embeddings)}")

            # print(f"First embedding sample (first 5 values): {embeddings[0][:5]}") if embeddings else print("No embeddings found.")

            if len(embeddings) != len(data):
                return f"Error: Mismatch between data ({len(data)}) and embeddings ({len(embeddings)})"

            vectors = []
            for d, e in zip(data, embeddings):
                if e is not None and isinstance(e, list):
                    # print(f"Embedding for id {d['id']} has length {len(e)}")
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
                # print(f"Skipping invalid embedding for id {d['id']} (embedding is None or not a list)")

            # print(f"Vectors prepared for upsert: {len(vectors)} vectors")
            if vectors:
                pass
                # print(f"Sample vector: {vectors[0]}")

            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

            index = pc.Index(index_name)

            if not vectors:
                print(
                    "No valid vectors to upsert (all embeddings may have failed or were invalid)."
                )
                return None

            res = index.upsert(
                vectors=vectors,
                namespace=namespace
                )
            print(
                f"SUCCESS: {len(vectors)} vectors were added. Pinecone response: {res}"
            )
            return "success"

        except Exception as e:
            print(f"Erro while storing : {e}")
            return "error"

