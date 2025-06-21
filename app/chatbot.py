from flask import (
    Flask,
    render_template,
    Response,
    jsonify,
    request,
    url_for,
    redirect,
    stream_with_context,
)
from flask_cors import CORS
from datetime import datetime
from werkzeug.utils import secure_filename
from nltk import sent_tokenize
import time
import re
import os

app = Flask(__name__)
CORS(app)


index_name = ""
starting_page = 0

context = None

app.config["UPLOAD_FOLDER"] = os.path.join("app", "data", "uploads")


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


@app.route("/chat/import-file", methods=["POST"])
@app.route("/chat/<conversation_id>/import-file", methods=["POST"])
def import_file(conversation_id=None):
    global index_name, starting_page

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

        today_str = datetime.now().strftime("%Y-%m-%d")
        folder_path = os.path.join(app.config["UPLOAD_FOLDER"], today_str)
        os.makedirs(folder_path, exist_ok=True)

        file_name = secure_filename(file.filename)
        file_path = os.path.join(folder_path, file_name)
        file.save(file_path)

        from app.agents.rag_agent.rag_agent import RAGAgent

        print(
            f"""
            file path = {file_path}    
            index_name = {index_name}
            start_page = {starting_page}"""
        )

        try:
            result = RAGAgent.import_file(file_path, index_name, starting_page)
        except Exception as e:
            print(e)

        if result == "success":
            # print(
            #     f"""
            # file path = {file_path}    
            # index_name = {index_name}
            # start_page = {starting_page}"""
            # )

            return jsonify({"message": "File added successfully", "status": "success"})
        else:
            return jsonify({"message": "Failed to process PDF"}), 500

    except Exception as e:
        print(f"Error during file importing : {e}")
        return (
            jsonify(
                {
                    "message": "Error during file import",
                    "status": "error",
                    "error_msg": f"Something went wrong while importing file : {e}",
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
