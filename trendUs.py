from flask import  Flask, request, jsonify, send_from_directory
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
import random
import difflib

def chat_ai(user_input):
    # 1️⃣ Clean the user input
    text = user_input.strip().lower()

    # 2️⃣ Define common greeting patterns
    greetings = [
        "hi", "hello", "hey", "hiya", "yo", "howdy",
        "good morning", "good afternoon", "good evening",
        "what's up", "sup", "greetings"
    ]

    # 3️⃣ Define possible replies
    replies = ["wagwan 😊"
        "sup 😊",
        "Hey How’s your day going?",
        "Hi Nice to see you.",
        "Good to have you here",
        "Greetings 👋",
        "Hey hey What’s up?",
        "Hope you’re set today"
    ]

    # 4️⃣ Use fuzzy matching to find close matches
    match = difflib.get_close_matches(text, greetings, n=1, cutoff=0.5)

    # 5️⃣ Add keyword detection for flexible understanding
    if any(word in text for word in ["morning", "afternoon", "evening", "night"]):
        if "morning" in text:
            return random.choice([
                " morning 🌅",
                "Morning Hope yo night was tight ",
                "A fresh morning to ya"
            ])
        elif "afternoon" in text:
            return random.choice([
                "Good afternoon ☀️",
                "Hope your afternoon’s going well",
                "Lovely afternoon, isn’t it?"
            ])
        elif "evening" in text or "night" in text:
            return random.choice([
                "Good evening 🌙",
                "Evening vibes Hope you’re relaxing.",
                "Good night Rest well when you do"
            ])

    # 6️⃣ If a fuzzy match found → reply with a random greeting
    if match:
        return random.choice(replies)

    # 7️⃣ If no match but user said *something*, still greet kindly
    return random.choice([
        "wagwan 😊",
        "ki-naye",
        "yo set?",
        "Hey What’s up?",
        "kinaye-bloodii 👋"
    ])

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
