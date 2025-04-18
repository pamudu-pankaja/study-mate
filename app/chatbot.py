from vector_store.file_load import load_pdf

file_path = "D:/Programming/Code Jam 2025/Hisory Chat Bot/history-chat-bot/app/data/8_grade-11-history-text-book.pdf"
chunk_size = 750
chunk_overlap = 60
result = load_pdf(file_path=file_path,chunk_overlap=chunk_overlap,chunk_size=chunk_size)

from vector_store.pinecorn_client import pinecone_db

response = pinecone_db.create_index()
upsert = pinecone_db.upsert(data=result)

print(upsert)
