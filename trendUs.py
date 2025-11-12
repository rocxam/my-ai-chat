from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os
import random
import difflib

# -----------------------------
# Cloudinary Configuration
# -----------------------------
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__, static_folder='.', template_folder='templates')
CORS(app)

# -----------------------------
# Simple AI Function
# -----------------------------
def chat_ai(user_input):
    text = user_input.strip().lower()

    greetings = [
        "hi", "hello", "hey", "hiya", "yo", "howdy",
        "good morning", "good afternoon", "good evening",
        "what's up", "sup", "greetings"
    ]

    replies = [
        "Wagwan 😊",
        "Sup 😊",
        "Hey! How’s your day going?",
        "Hi! Nice to see you.",
        "Good to have you here.",
        "Greetings 👋",
        "Hey hey! What’s up?",
        "Hope you’re set today!"
    ]

    match = difflib.get_close_matches(text, greetings, n=1, cutoff=0.5)

    if any(word in text for word in ["morning", "afternoon", "evening", "night"]):
        if "morning" in text:
            return random.choice([
                "Morning 🌅",
                "Morning! Hope your night was tight!",
                "A fresh morning to ya ☀️"
            ])
        elif "afternoon" in text:
            return random.choice([
                "Good afternoon ☀️",
                "Hope your afternoon’s going well!",
                "Lovely afternoon, isn’t it?"
            ])
        elif "evening" in text or "night" in text:
            return random.choice([
                "Good evening 🌙",
                "Evening vibes! Hope you’re relaxing.",
                "Good night — rest well when you do!"
            ])

    if match:
        return random.choice(replies)

    return random.choice([
        "Wagwan 😊",
        "Ki-naye 👋",
        "Yo set?",
        "Hey! What’s up?",
        "Kinaye-bloodii 👋"
    ])

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if data and 'message' in data:
        user_input = data.get('message', '')
        reply = chat_ai(user_input)
        return jsonify({'reply': reply})
    return jsonify({'reply': "Send a message."})

# -----------------------------
# Campus Manager Route
# -----------------------------
@app.route('/campus')
def campus():
    return render_template('campus.html')

# -----------------------------
# File Serving (Optional for Static)
# -----------------------------
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
