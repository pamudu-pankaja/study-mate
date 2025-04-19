from pinecone import Pinecone,ServerlessSpec
from config.config import PINECORN_API_KEY
import time

pc = Pinecone(api_key=PINECORN_API_KEY)


class pinecone_db():
    @staticmethod
    def create_index(index_name):        

        try:
            if index_name not in pc.list_indexes():
                pc.create_index(
                name=index_name,
                dimension=768,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            return "CREAT INDEX SUCCESSFUL"
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                return "WORKING ON A ALREADY EXISTS INDEX"
            else:
                return f"Error while requasting : {e}"
    @staticmethod    
    def upsert(data,index_name):
        from agents.rag_agent.vector_store.embedder import Embedding

        try:
            data_texts = [d['text'] for d in data]
            embeddings = Embedding.get_embedding_chunks(data_texts)

            while not pc.describe_index(index_name).status['ready']:
                time.sleep(1)

            index = pc.Index(index_name)

            vectors = []
            for d, e in zip(data, embeddings):
                if e is not None:
                    vectors.append({
                        'id' : d['id'],
                        'values' : e,
                        'metadata' : {'text': d['text']}
                    })

            index.upsert(
                vectors=vectors,
            )
            return f" SUCCESS : {len(vectors)} Vectors were added"
        except Exception as e:
            return f"Erro while storing : {e}"

