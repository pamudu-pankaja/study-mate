from app.chatbot import app
import os
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["BASE_DIR"] = BASE_DIR
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "tmp/uploads")
app.config["MAIL_FILE"] = os.path.join(BASE_DIR, "chat/mails.json")
app.config["PINECONE_DATA_FILE"] = os.path.join(BASE_DIR , "chat/pinecone_data.json")
app.config["BOOK_FILE"] = os.path.join(BASE_DIR, "chat/books.json")

if __name__ == "__main__":
    # webbrowser.open_new_tab("http://127.0.0.1:5000")
    app.run(debug=True)

