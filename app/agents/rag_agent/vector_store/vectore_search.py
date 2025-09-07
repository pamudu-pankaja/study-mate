from app.agents.rag_agent.vector_store.embedder import Embed_text
from app.agents.rag_agent.vector_store.file_load import detect_language
from app.config.config import PINECORN_API_KEY
from pinecone import Pinecone

pc = Pinecone(api_key=PINECORN_API_KEY)


def search(query, book_name):
    index = pc.Index("text-books")

    lang = detect_language(query)
    print("Getting the embeddings of the query...")
    query_vector = Embed_text.embed_query(query, lang)

    results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True,
        include_values=False,
        namespace=book_name,
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
