from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='')

def chat_ai(user_input):
    if user_input.lower() == "hi":
        return "hello"
    else:
        return "I only reply to 'hi' 🙂"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    reply = chat_ai(user_input)
    return jsonify({'reply': reply})

@app.route('/')
def home():
    return send_from_directory('.', 'chat.html')

if __name__ == '__main__':
    app.run(debug=True)
