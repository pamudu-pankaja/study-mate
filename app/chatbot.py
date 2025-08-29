from flask import (
    Flask,
    render_template,
    Response,
    jsonify,
    request,
    url_for,
    redirect,
    current_app,
)

from flask_cors import CORS
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import time
import os
import threading


app = Flask(__name__)
CORS(app)


book_name = ""
context = None


def ensure_mail_file(mail_file):
    if not os.path.exists(mail_file):
        with open(mail_file, "w", encoding="utf-8") as f:
            json.dump([], f)
            
def ensure_books_file(BOOKS_FILE):
    if not os.path.exists(BOOKS_FILE):
        os.makedirs(os.path.dirname(BOOKS_FILE), exist_ok=True)
        default_books = {
            "systemBooks": [],
            "userBooks": []
        }
        
        with open(BOOKS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_books, f, indent=2, ensure_ascii=False)
        print("books.json initialized with default data")

def ensure_pinecone_data_file(PINECONE_DATA_FILE):
    if not os.path.exists(PINECONE_DATA_FILE):
        os.makedirs(os.path.dirname(PINECONE_DATA_FILE), exist_ok=True)
        default_data = {
            "booksWithData": []
        }
        
        with open(PINECONE_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        print("pinecone_data.json initialized with default data")

def read_pinecone_data(PINECONE_DATA_FILE):
    try:
        with open(PINECONE_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading pinecone data file: {e}")
        return {"booksWithData": []}

def write_pinecone_data(pinecone_data, PINECONE_DATA_FILE):
    try:
        with open(PINECONE_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(pinecone_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing pinecone data file: {e}")
        return False

def add_book_to_pinecone_data(book_name, PINECONE_DATA_FILE):
    data = read_pinecone_data(PINECONE_DATA_FILE)
    if book_name not in data["booksWithData"]:
        data["booksWithData"].append(book_name)
        write_pinecone_data(data, PINECONE_DATA_FILE)

def remove_book_from_pinecone_data(book_name, PINECONE_DATA_FILE):
    data = read_pinecone_data(PINECONE_DATA_FILE)
    if book_name in data["booksWithData"]:
        data["booksWithData"].remove(book_name)
        write_pinecone_data(data, PINECONE_DATA_FILE)

def process_mail_file(file_path, book_name, starting_page: int, file_name, mail_file, pinecone_data_file):
    try:
        from app.agents.rag_agent.rag_agent import RAGAgent

        print(f"Background processing started for {file_name}")

        result = RAGAgent.import_file(file_path, book_name, starting_page)

        if result == "success":
            add_book_to_pinecone_data(book_name, pinecone_data_file)
            save_mail(
                "System",
                f"File '{file_name}' has been successfully processed and ready to use",
                mail_file_path=mail_file,
            )
            print(f"Background processing completed successfully for {file_name}")
        else:
            save_mail(
                "System",
                f"Failed to process file '{file_name}'. Please try again",
                mail_file_path=mail_file,
            )
            print(f"Background processing failed for {file_name}")

    except Exception as e:
        save_mail(
            "System",
            f"Error processing file '{file_name}': {str(e)}",
            mail_file_path=mail_file,
        )
        print(f"Background processing error for {file_name}: {e}")
        
def read_books(BOOKS_FILE):
    try:
        with open(BOOKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading books file: {e}")
        return {"systemBooks": [], "userBooks": []}

def write_books(books_data, BOOKS_FILE):
    try:
        with open(BOOKS_FILE, "w", encoding="utf-8") as f:
            json.dump(books_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing books file: {e}")
        return False


@app.context_processor
def override_url_for():
    def dated_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.static_folder, filename)
                if os.path.isfile(file_path):
                    values['v'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)
    return dict(url_for=dated_url_for)

@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("chat_page"))


@app.route("/chat", methods=["GET"])
def chat_page():
    return render_template("index.html")


@app.route("/chat/", methods=["GET"])
def chat_page_slash():
    return redirect(url_for("chat_page"))

@app.route("/disabled-feature")
def disabled_feature():
    return render_template("disabled-feature.html")


@app.route("/chat/<conversation_id>", methods=["GET"])
def chat_page_with_id(conversation_id):
    if not conversation_id:
        return redirect(url_for("chat_page"))
    return render_template("index.html", chat_id=conversation_id)


@app.route("/chat/generate-title", methods=["POST"])
@app.route("/chat/<conversation_id>/generate-title", methods=["POST"])
def get_title(conversation_id=None):
    data = request.json
    user_msg = data.get("message", "")

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    from app.agents.llm.llm import GeminiLLM

    title = GeminiLLM.generate_title(user_msg)
    print(f"Sending Title : {title}")
    return jsonify({"title": title})


@app.route("/chat/context-data", methods=["GET"])
@app.route("/chat/<conversation_id>/context-data", methods=["GET"])
def get_context(conversation_id=None):
    global context
    print("Sending Context Data...")

    return jsonify({"context": context if context is not None else "None"})


@app.route("/chat", methods=["POST"])
@app.route("/chat/<conversation_id>", methods=["POST"])
def chat_req(conversation_id=None):
    global book_name, context
    try:
        data = request.get_json()

        print("Received:", data["meta"]["content"]["parts"][0]["content"])

        user_message = data["meta"]["content"]["parts"][0]["content"]
        path = data["searchPath"]
        
        def event_stream():
            for word in reply.split():
                time.sleep(0.1)
                yield f"data: {word} \n\n"

        if path == "none":
            path = None
        else:
            path = path

        if path == "vector" and book_name == "":
            reply = "Please set a valid Book name , using the side bar "
            print("Sending:", reply)
            return Response(event_stream(), mimetype="text/event-stream"), 500
        
        if path == "vector" and book_name != "":
            pinecone_data_file = current_app.config["PINECONE_DATA_FILE"]
            ensure_pinecone_data_file(pinecone_data_file)
            pinecone_data = read_pinecone_data(pinecone_data_file)
            
            if book_name not in pinecone_data["booksWithData"]:
                reply = "Your selected Book name dosent have any files imported or it must be an invalid one. Please select a valid book or import some files"
                print("Sending:", reply)
                return Response(event_stream(), mimetype="text/event-stream"), 500
            else: 
                pass            

        from app.agents import ChatBotAgent

        response = ChatBotAgent.get_response(
            user_message, path=path, chat_history=data, book_name=book_name
        )

        reply = response["reply"]
        context = response["context"]

        if reply.startswith("Answer:"):
            reply = reply[len("Answer:") :].strip()

        reply = reply.replace(
            "Pages and Sections:", "Relevant Pages and Sections Below 👇"
        )
        reply = reply.replace("- Pages:", "- 📄 Pages:")
        reply = reply.replace("- Sections:", "- 📚 Sections:")

        if path == None:

            def event_stream():
                for chunk in reply.splitlines():
                    yield f"data: {chunk}\n\n"
                    time.sleep(0.1)

        else:

            def event_stream():
                for word in reply.splitlines():
                    yield f"data: {word} \n\n"
                    time.sleep(0.1)

        print("\nSending:", "\n" + reply)

        return Response(event_stream(), mimetype="text/event-stream")

    except Exception as e:
        print(e)
        reply = "Something went wrong while answering"

        def event_stream():
            for word in reply.split():
                time.sleep(0.1)
                yield f"data: {word} \n\n"

        print("Sending:", reply)

        return Response(event_stream(), mimetype="text/event-stream"), 500


@app.route("/chat/book-name", methods=["POST"])
@app.route("/chat/<conversation_id>/book-name", methods=["POST"])
def book_name_post(conversation_id=None):
    global book_name
    try:
        data = request.get_json()
        book_name = data.get("book_name")

        if not book_name:
            book_name = ""
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Something went wrong",
                        "error_msg": "book_name not provided",
                    }
                ),
                400,
            )

        print(f"Book Name updated : {book_name}")
        return jsonify(
            {"status": "success", "message": "Book name successfully updated"}
        )

    except Exception as e:
        print(f"Something went wrong while getting namespace : {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Something went wrong",
                    "error_msg": str(e),
                }
            ),
            500,
        )


@app.route("/chat/book-name", methods=["GET"])
@app.route("/chat/<conversation_id>/book-name", methods=["GET"])
def book_name_get(conversation_id=None):
    global book_name
    if book_name:
        print(f"Sending... book name : {book_name} ")
        return jsonify(
            {"book_name": f"{book_name}", "bookName": book_name}
        )
    if not book_name:
        return jsonify({"book_name": "TextBook Not Selected", "BookName": book_name})


def save_mail(sender, content, mail_file_path, seen=False):
    mail_file = mail_file_path

    if os.path.exists(mail_file):
        with open(mail_file, "r") as f:
            mails = json.load(f)
    else:
        mails = []

    next_id = max([mail.get("id", 0) for mail in mails], default=0) + 1

    new_mail = {
        "id": next_id,
        "sender": sender,
        "content": content,
        "seen": seen,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    mails.append(new_mail)

    with open(mail_file, "w") as f:
        json.dump(mails, f, indent=2)

    print(f"Mail saved: {content}")


@app.route("/chat/import-file", methods=["POST"])
@app.route("/chat/<conversation_id>/import-file", methods=["POST"])
def import_file(conversation_id=None):
    global book_name
    starting_page = 0
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    mail_file = current_app.config["MAIL_FILE"]
    pinecone_data_file = current_app.config["PINECONE_DATA_FILE"]
    
    book_file = current_app.config["BOOK_FILE"]
    ensure_books_file(book_file)
    ensure_pinecone_data_file(pinecone_data_file)      
    
    books = read_books(book_file)
    system_books = books.get("systemBooks", [])
    
    if book_name in system_books :
        return jsonify({"message":"You cannot update system books" , "status" : "error"}),400

    try:
        if "pdf" not in request.files:
            print("error : No file has given ")
            return jsonify({"message": "No file has given", "status": "error"}), 400

        file = request.files["pdf"]
        if file.filename == "":
            print("error :  No file has selected")
            return jsonify({"message": "No file has selected", "status": "error"}), 400

        start_page = request.form.get("startPage")
        starting_page = (
            int(start_page) if start_page and start_page.strip() != "" else 0
        )

        folder_path = upload_folder
        os.makedirs(folder_path, exist_ok=True)

        file_name = secure_filename(file.filename)
        file_path = os.path.join(folder_path, file_name)
        file.save(file_path)

        print(
            f"""
file path = {file_path}    
book_name = {book_name}
start_page = {starting_page}
Starting Background processing..."""
        )

        thread = threading.Thread(
            target=process_mail_file,
            args=(file_path, book_name, starting_page, file_name, mail_file, pinecone_data_file),
            daemon=True,
        )
        thread.start()

        save_mail(
            "System",
            f"File '{file_name}' ,  received and queued for processing. You'll be notified when it's ready!",
            mail_file_path=mail_file,
        )

        return (
            jsonify(
                {
                    "message": f"File '{file_name}' is being processed in the background. Check your notifications for updates.",
                    "status": "processing",
                    "file_name": file_name,
                }
            ),
            202,
        )

    except Exception as e:
        print(f"Error during file importing: {e}")
        save_mail(
            "System", f"Error uploading file: {str(e)}", mail_file_path=mail_file
        )
        return (
            jsonify(
                {
                    "message": "Error during file upload",
                    "status": "error",
                    "error_msg": f"Something went wrong: {e}",
                }
            ),
            500,
        )

@app.route("/chat/mail", methods=["GET"])
@app.route("/chat/<conversation_id>/mail", methods=["GET"])
def get_message(conversation_id=None):
    mail_file = current_app.config["MAIL_FILE"]
    ensure_mail_file(mail_file)

    with open(mail_file, "r", encoding="utf-8") as f:
        message = json.load(f)
    return jsonify(message)


@app.route("/chat/mail/<int:msg_id>", methods=["DELETE"])
@app.route("/chat/<conversation_id>/mail/<int:msg_id>", methods=["DELETE"])
def delete_message(msg_id, conversation_id=None):
    mail_file = current_app.config["MAIL_FILE"]
    ensure_mail_file(mail_file)

    if not os.path.exists(mail_file):
        return jsonify({"status": "error", "message": "No mail file found"}), 404
    with open(mail_file, "r", encoding="utf-8") as f:
        messages = json.load(f)
    messages = [m for m in messages if m.get("id") != msg_id]
    with open(mail_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)
    return jsonify({"status": "success"}), 200


@app.route("/chat/mail/mark-seen", methods=["POST"])
@app.route("/chat/<conversation_id>/mail/mark-seen", methods=["POST"])
def mark_mail_seen(conversation_id=None):
    mail_file = current_app.config["MAIL_FILE"]
    ensure_mail_file(mail_file)
    try:
        with open(mail_file, "r", encoding="utf-8") as f:
            messages = json.load(f)
        for msg in messages:
            msg["seen"] = True
        with open(mail_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/chat/books/list", methods=["GET"])
@app.route("/chat/<conversation_id>/books/list", methods=["GET"])
def get_books_list(conversation_id=None):
    book_file = current_app.config["BOOK_FILE"]
    ensure_books_file(book_file)
    try:
        books = read_books(book_file)
        system_books = books.get("systemBooks", [])
        user_books = books.get("userBooks", [])
        
        return jsonify({
            "success": True,
            "systemBooks": system_books,
            "userBooks": user_books,
            "totalCount": len(system_books) + len(user_books)
        })
    except Exception as e:
        print(f"Error fetching books: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch books",
            "error": str(e)
        }), 500

@app.route("/chat/books/add", methods=["POST"])
@app.route("/chat/<conversation_id>/books/add", methods=["POST"])
def add_book(conversation_id=None):
    book_file = current_app.config["BOOK_FILE"]
    ensure_books_file(book_file)
    try:
        data = request.get_json()
        book_name = data.get("bookName", "").strip()
        
        if not book_name:
            return jsonify({
                "success": False,
                "message": "Book name is required"
            }), 400
        
        books = read_books(book_file)
        
        all_books = books.get("systemBooks", []) + books.get("userBooks", [])
        book_exists = any(book.lower() == book_name.lower() for book in all_books)
        
        if book_exists:
            return jsonify({
                "success": False,
                "message": "Book already exists"
            }), 409

        if "userBooks" not in books:
            books["userBooks"] = []
        books["userBooks"].append(book_name)
        
        if write_books(books, book_file):
            print(f"Book added: {book_name}")
            return jsonify({
                "success": True,
                "message": "Book added successfully",
                "bookName": book_name
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to save book"
            }), 500
            
    except Exception as e:
        print(f"Error adding book: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to add book",
            "error": str(e)
        }), 500

@app.route("/chat/books/delete", methods=["DELETE"])
@app.route("/chat/<conversation_id>/books/delete", methods=["DELETE"])
def delete_book(conversation_id=None):
    book_file = current_app.config["BOOK_FILE"]
    pinecone_data_file = current_app.config["PINECONE_DATA_FILE"]
    ensure_books_file(book_file)
    ensure_pinecone_data_file(pinecone_data_file)
    try:
        data = request.get_json()
        book_name = data.get("bookName", "").strip()
       
        if not book_name:
            return jsonify({
                "success": False,
                "message": "Book name is required"
            }), 400
       
        books = read_books(book_file)
        pinecone_data = read_pinecone_data(pinecone_data_file)
       
        is_system_book = any(
            book.lower() == book_name.lower()
            for book in books.get("systemBooks", [])
        )
       
        if is_system_book:
            return jsonify({
                "success": False,
                "message": "Cannot delete system books"
            }), 403
       
        user_books = books.get("userBooks", [])
        book_index = -1
        for i, book in enumerate(user_books):
            if book.lower() == book_name.lower():
                book_index = i
                break
        
        book_in_file = book_index != -1
        book_in_pinecone = book_name in pinecone_data["booksWithData"]
       
        if not book_in_file and not book_in_pinecone:
            return jsonify({
                "success": False,
                "message": "Book not found"
            }), 404
       
        deleted_from = []
        
        if book_in_file:
            removed_book = user_books.pop(book_index)
            books["userBooks"] = user_books
            
            if write_books(books, book_file):
                deleted_from.append("file")
                print(f"Book deleted from file: {removed_book}")
            else:
                return jsonify({
                    "success": False,
                    "message": "Failed to delete book"
                }), 500
        
        if book_in_pinecone:
            try:
                from pinecone import Pinecone
                from app.config.config import PINECORN_API_KEY
                
                pc = Pinecone(api_key=PINECORN_API_KEY)
                index = pc.Index("text-books")
                index.delete(delete_all=True, namespace=book_name)
                
                remove_book_from_pinecone_data(book_name, pinecone_data_file)
                deleted_from.append("Pinecone")
                print(f"Book deleted from Pinecone: {book_name}")
            except Exception as e:
                print(f"Error deleting from Pinecone: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"Failed to delete book: {str(e)}"
                }), 500
        
        return jsonify({
            "success": True,
            "message": "Book deleted successfully",
            "bookName": book_name,
            "deletedFrom": deleted_from
        })
       
    except Exception as e:
        print(f"Error in delete_book: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }), 500

@app.route("/chat/books/system", methods=["GET"])
@app.route("/chat/<conversation_id>/books/system", methods=["GET"])
def get_system_books(conversation_id=None):
    book_file = current_app.config["BOOK_FILE"]
    ensure_books_file(book_file)
    try:
        books = read_books(book_file)
        return jsonify({
            "success": True,
            "books": books.get("systemBooks", [])
        })
    except Exception as e:
        print(f"Error fetching system books: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch system books",
            "error": str(e)
        }), 500

@app.route("/chat/books/user", methods=["GET"])
@app.route("/chat/<conversation_id>/books/user", methods=["GET"])
def get_user_books(conversation_id=None):
    book_file = current_app.config["BOOK_FILE"]
    ensure_books_file(book_file)
    try:
        books = read_books(book_file)
        return jsonify({
            "success": True,
            "books": books.get("userBooks", [])
        })
    except Exception as e:
        print(f"Error fetching user books: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch user books",
            "error": str(e)
        }), 500