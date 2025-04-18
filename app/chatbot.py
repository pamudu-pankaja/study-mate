query = "Who did the type setting on this book ?"
index_name = "history-text"

from vector_store.vectore_search import search

result = search(query,index_name)

print(result)


# from vector_store.file_load import load_pdf

# file_path = "D:/Programming/Code Jam 2025/Hisory Chat Bot/history-chat-bot/app/data/3_grade-11-history-text-book.pdf"
# result = load_pdf(file_path=file_path)

# from vector_store.pinecorn_client import pinecone_db

# response = pinecone_db.create_index()
# upsert = pinecone_db.upsert(data=result)

# print(upsert)