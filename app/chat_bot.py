# from flask import Flask, render_template_string, send_from_directory,request,session

# app = Flask(__name__)

# @app.route("/")
# def home():
#     with open("app/client/html/index.html") as f:
#         html = f.read()
#     return render_template_string(html, chat_id="123", url_prefix="", _=lambda x: x)

# @app.route('/css/<path:filename>')
# def css(filename):
#     return send_from_directory('client/css', filename)

# @app.route('/js/<path:filename>')
# def js(filename):
#     return send_from_directory('client/js', filename)

# @app.route('/img/<path:filename>')
# def img(filename):
#     return send_from_directory('client/img', filename)

# @app.route('/chat',methods=['POST'])
# def chat():
#     user_message = request.json.get('messages')
#     print(user_message)
    
#     bot_response = "Hello, you said: " + user_message

#     # Store chat history in session (optional, you can skip if you don't need it)
#     if 'messages' not in session:
#         session['messages'] = []

#     # Save both user and bot messages to the session
#     session['messages'].append({'user': user_message, 'bot': bot_response})

#     # Return the conversation history (including the new user and bot message)

# if __name__ == "__main__":
#     app.run(debug=True)

