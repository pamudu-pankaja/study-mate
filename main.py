from app.chatbot import app
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["BASE_DIR"] = BASE_DIR
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "tmp/uploads")
app.config["OFFSET_FILE"] = os.path.join(BASE_DIR, "page_offsets.json")
app.config["MAIL_FILE"] = os.path.join(BASE_DIR, "mails.json")

if __name__ == "__main__":
    app.run(debug=True)
