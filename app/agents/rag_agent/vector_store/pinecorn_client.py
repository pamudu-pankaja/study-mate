from pinecone import Pinecone, ServerlessSpec
from app.config.config import PINECORN_API_KEY
import time

pc = Pinecone(api_key=PINECORN_API_KEY)


class pinecone_db:
    @staticmethod
    def create_index(index_name):

        try:
            if index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            return f"Successfully created the index : {index_name}"
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                pass
            else:
                return f"Error while requasting : {e}"

    @staticmethod
    def create_embedding_text(chunk_data):
        text = chunk_data["text"]
        section = chunk_data.get("section", "")
        page = chunk_data.get("page", "")

        if section and page:
            return f"Section: {section} | Page: {page} | Content: {text}"
        elif section:
            return f"Section: {section} | Content: {text}"
        elif page:
            return f"Page: {page} | Content: {text}"
        else:
            return text

    @staticmethod
    def upsert(data, namespace, index_name="text-books", batch_size=500):

        pinecone_db.create_index(index_name)

        from app.agents.rag_agent.vector_store.embedder import Embedding

        try:
            data = [
                d for d in data if isinstance(d, dict) and "text" in d and "id" in d
            ]

            # includes section and page
            embedding_texts = [pinecone_db.create_embedding_text(d) for d in data]

            print("Embedding the Chunks...")
            embeddings = Embedding.get_embedding_chunks(embedding_texts)

            if len(embeddings) != len(data):
                print(
                    f"Error: Mismatch between data ({len(data)}) and embeddings ({len(embeddings)})"
                )
                return "error"

            vectors = []
            for d, e in zip(data, embeddings):
                if e is not None and isinstance(e, list) and len(e) == 768:
                    vectors.append(
                        {
                            "id": str(d["id"]),
                            "values": e,
                            "metadata": {
                                "text": d["text"],
                                "page": str(d.get("page", "")),
                                "section": str(d.get("section", "")),
                            },
                        }
                    )
                else:
                    print(f"Invalid embedding for id {d['id']}. Skipping..")

            if not vectors:
                print("No valid vectors to upsert.")
                return None

            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

            index = pc.Index(index_name)

            # Batch upsert in chunks of 500
            print("Upserting...")
            total_upserted = 0
            for i in range(0, len(vectors), batch_size):
                batch_vectors = vectors[i : i + batch_size]

                attempt = 0
                while True:
                    try:
                        res = index.upsert(vectors=batch_vectors, namespace=namespace)
                        total_upserted += len(batch_vectors)
                        print(
                            f"Upserted batch {i//batch_size+1}: {len(batch_vectors)} vectors"
                        )
                        print(f"Pinecone response : {res}")
                        break
                    except Exception as e:
                        attempt += 1
                        wait = min(60, 2**attempt)
                        print(
                            f"Error on upsert batch {i//batch_size+1}: {e} | retrying in {wait}s"
                        )
                        time.sleep(wait)

            print(
                f"Success: {total_upserted} total vectors upserted to namespace '{namespace}'"
            )

            return "success"

        except Exception as e:
            print(f"Error while storing: {e}")
            return "error"
