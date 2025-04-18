from pinecone import Pinecone,ServerlessSpec
from config.config import PINECORN_API_KEY
import time

pc = Pinecone(api_key=PINECORN_API_KEY)
index_name = "history-text"

class pinecone_db():
    def create_index():        

        try:
            if index_name not in pc.list_indexes():
                pc.create_index(
                name=index_name,
                dimension=1024,
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
            
    def upsert(data):

        try:
            embeddings = pc.inference.embed(
                model="multilingual-e5-large",
                inputs=[d['text'] for d in data],
                parameters={"input_type": "passage", "truncate": "END"}
            )
            print(embeddings[0])

            while not pc.describe_index(index_name).status['ready']:
                time.sleep(1)

            index = pc.Index(index_name)

            vectors = []
            for d, e in zip(data, embeddings):
                vectors.append({
                    'id' : d['id'],
                    'values' : e['values'],
                    'metadata' : {'text': d['text']}
                })

            index.upsert(
                vectors=vectors,
                namespace="ns1"
            )
            return f" SUCCESS : {len(vectors)} Vectors were added"
        except Exception as e:
            return f"Erro while storing : {e}"

