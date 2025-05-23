from flask import Flask, render_template , Response , jsonify , request , url_for , redirect
from flask_cors import CORS
import json
import time

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat" , methods=["GET"])
def chat_page():
    return render_template("index.html" )

@app.route("/chat/<conversation_id>")
def chat_page_with_id(conversation_id):
    if not conversation_id:
        return redirect(url_for("chat_page"))
    return render_template("index.html" , chat_id = conversation_id) 

@app.route('/chat' , methods=['POST'])    
@app.route('/chat/<conversation_id>' , methods=['POST'])
def chat_req(conversation_id=None):
    try:
        data = request.get_json()
        print("Received:", data["meta"]["content"]["parts"][0]["content"])

        user_message = data["meta"]["content"]["parts"][0]["content"]

        reply = "HELOOO dudee ! How are you doing ?, it is great that you can see this response "

        def event_stream():
            for word in reply.split():
                time.sleep(0.1)
                yield f"data: {word} \n\n"
                

        return Response(event_stream(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == "__main__":
    app.run(debug=True)