from app.agents.rag_agent.vector_store.embedder import Embedding
from app.config.config import PINECORN_API_KEY
from pinecone import Pinecone

pc = Pinecone(api_key=PINECORN_API_KEY)


def search(query, index_name):
    index = pc.Index(index_name)

    print("Getting the embeddings of the query...")

    query_vector = Embedding.get_embedding_query(
        query=query
    )  # + "include page numbers and sections")

    results = index.query(
        vector=query_vector, top_k=5, include_metadata=True, include_values=False
    )

    data = []

    for match in results["matches"]:
        data.append(
            {
                "text": match["metadata"].get("text", ""),
                "page": match["metadata"].get("page", "unknown"),
                "section": match["metadata"].get("section", "unknown"),
            }
        )

    # print()
    # print(data)
    # print()
    return data
