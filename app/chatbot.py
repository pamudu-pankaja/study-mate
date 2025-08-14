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


index_name = ""
starting_page = 0

context = None


def ensure_mail_file(mail_file):
    if not os.path.exists(mail_file):
        with open(mail_file, "w", encoding="utf-8") as f:
            json.dump([], f)


@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("chat_page"))


@app.route("/chat", methods=["GET"])
def chat_page():
    return render_template("index.html")


@app.route("/chat/", methods=["GET"])
def chat_page_slash():
    return redirect(url_for("chat_page"))


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
    global index_name, context
    try:
        data = request.get_json()

        print("Received:", data["meta"]["content"]["parts"][0]["content"])
        # print(data)

        user_message = data["meta"]["content"]["parts"][0]["content"]
        path = data["searchPath"]

        if path == "none":
            path = None
        else:
            path = path

        if path == "vector" and index_name == "":
            reply = "Please set a valid index name , using the side bar "

            def event_stream():
                for word in reply.split():
                    time.sleep(0.1)
                    yield f"data: {word} \n\n"

            print("Sending:", reply)

            return Response(event_stream(), mimetype="text/event-stream"), 500

        from app.agents import ChatBotAgent

        response = ChatBotAgent.get_response(
            user_message, path=path, chat_history=data, index_name=index_name
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


@app.route("/chat/index-name", methods=["POST"])
@app.route("/chat/<conversation_id>/index-name", methods=["POST"])
def index_name_post(conversation_id=None):
    global index_name
    try:
        data = request.get_json()
        index_name = data.get("index_name")

        if not index_name:
            index_name = ""
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Something went wrong",
                        "error_msg": "index_name not provided",
                    }
                ),
                400,
            )

        print(f"Index Name updated : {index_name}")
        return jsonify(
            {"status": "success", "message": "Index name successfully updated"}
        )

    except Exception as e:
        print(f"Something went wrong while getting index : {e}")
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


@app.route("/chat/index-name", methods=["GET"])
@app.route("/chat/<conversation_id>/index-name", methods=["GET"])
def index_name_get(conversation_id=None):
    global index_name
    if index_name:
        print(f"Sending... index name : {index_name} ")
        return jsonify(
            {"index_name": f"Index Name : {index_name}", "indexName": index_name}
        )
    if not index_name:
        print(f"Sending... Empty index name")
        return jsonify({"index_name": "Index Name : Not set", "indexName": index_name})


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


def process_file(file_path, index_name, starting_page: int, file_name, mail_file):
    try:
        from app.agents.rag_agent.rag_agent import RAGAgent

        print(f"Background processing started for {file_name}")

        result = RAGAgent.import_file(file_path, index_name, starting_page)

        if result == "success":
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


@app.route("/chat/import-file", methods=["POST"])
@app.route("/chat/<conversation_id>/import-file", methods=["POST"])
def import_file(conversation_id=None):
    global index_name, starting_page
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    mail_file = current_app.config["MAIL_FILE"]

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

        from app.agents.rag_agent.rag_agent import RAGAgent

        print(
            f"""
file path = {file_path}    
index_name = {index_name}
start_page = {starting_page}
Starting Background processing..."""
        )

        thread = threading.Thread(
            target=process_file,
            args=(file_path, index_name, starting_page, file_name, mail_file),
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
            "System", f"❌ Error uploading file: {str(e)}", mail_file_path=mail_file
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


@app.route("/chat/start-page", methods=["GET"])
@app.route("/chat/<conversation_id>/start-page", methods=["GET"])
def starting_page_get(conversation_id=None):
    global starting_page
    if starting_page > 0:
        print(f"Sending... start page : {starting_page} ")
        return jsonify(
            {"start_page": f"Start Page : {starting_page}", "startPage": starting_page}
        )

    else:
        print(f"Sending... start page : {starting_page} ")
        return jsonify({"start_page": "Start Page : Not set", "startPage": 0})


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
