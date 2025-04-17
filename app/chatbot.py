from app import astra_db

db = astra_db()

chunks = db.load_pdf("D:\Programming\Code Jam 2025\Hisory Chat Bot\history-chat-bot\app\data\Future Minds Problem Statement.pdf", chunk_size=250, chunk_overlap=20)
result = db.store_data(chunks,"future-mind-problem")

print(result)