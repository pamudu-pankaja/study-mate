from app.agents.rag_agent.vector_store.embedder import Embed_text
from app.agents.rag_agent.vector_store.file_load import detect_language
from app.config.config import PINECORN_API_KEY
from pinecone import Pinecone

pc = Pinecone(api_key=PINECORN_API_KEY)


def search(query, book_name):
    index = pc.Index("text-books")

    langs = detect_language(query)
    ocr_language = "+".join(langs) if langs else "eng"
    print("Getting the embeddings of the query...")
    print(f"Query Language : {ocr_language}")
    query_vector = Embed_text.embed_query(query, ocr_language)
    # print(f"Query Vector {query_vector}")

    results = index.query(
        vector=query_vector,
        top_k=10,
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

    print()
    print(data)
    print()
    return data
