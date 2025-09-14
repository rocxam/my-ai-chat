from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

app = Flask(__name__)
CORS(app)  # Important for frontend communication

def chat_ai(user_input):
    if user_input.lower() == "hi":
        return "hello"
    else:
        return "I only reply to 'hi' 🙂"

@app.route('/chat', methods=['POST'])
def chat():
    # Check for file upload
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            file_url = upload_result['secure_url']
            return jsonify({'reply': f"File uploaded! View it: {file_url}"})

    # Check for text message
    data = request.get_json()
    if data and 'message' in data:
        user_input = data.get('message', '')
        reply = chat_ai(user_input)
        return jsonify({'reply': reply})

    return jsonify({'reply': "Send a message or a file."})

@app.route('/')
def home():
    return send_from_directory('.', 'chat.html')

if __name__ == '__main__':
    app.run(debug=True)