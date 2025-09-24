from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os

# -----------------------------
# Cloudinary Configuration
# -----------------------------
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

app = Flask(__name__)
CORS(app)

# -----------------------------
# Simple AI Function
# -----------------------------
def chat_ai(user_input):
    if user_input.lower() == "hi":
        return "hello"
    else:
        return "I only reply to 'hi' 🙂"

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def home():
    return send_from_directory('.', 'chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Handle text message
    data = request.get_json()
    if data and 'message' in data:
        user_input = data.get('message', '')
        reply = chat_ai(user_input)
        return jsonify({'reply': reply})

    return jsonify({'reply': "Send a message."})

# -----------------------------
# Run app
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
