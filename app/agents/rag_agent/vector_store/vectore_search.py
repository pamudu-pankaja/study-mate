from agents.rag_agent.vector_store.embedder import Embedding
from config.config import PINECORN_API_KEY
from pinecone import Pinecone

def search(query,index_name):

    pc = Pinecone(api_key=PINECORN_API_KEY)
    index = pc.Index(index_name)

    query_vector = Embedding.get_embedding_query(query=query)

    result = index.query(
        vector=query_vector,
        top_k= 3,
        include_metadata=True,
        include_values=False
    )
    return result
    