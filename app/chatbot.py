from flask import Flask, render_template, Response, jsonify, request, url_for, redirect
from flask_cors import CORS
import json
import time

index_name = ""
starting_page = 0


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


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


@app.route("/chat", methods=["POST"])
@app.route("/chat/<conversation_id>", methods=["POST"])
def chat_req(conversation_id=None):
    try:
        data = request.get_json()
        print("Received:", data)

        user_message = data["meta"]["content"]["parts"][0]["content"]

        # from app.agents import ChatBotAgent
        # reply = ChatBotAgent.get_response(user_message,path=None)

        reply = (
            "Hello ! from back-end. how are you doing ? .I guess you are doing fine "
        )

        def event_stream():
            for word in reply.split():
                time.sleep(0.1)
                yield f"data: {word} \n\n"

        return Response(event_stream(), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"index_name": f"Index Name : {index_name}"})
    if not index_name:
        print(f"Sending... Empty index name")
        return jsonify({"index_name": "Index Name : Not set"})


# def main():
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)
