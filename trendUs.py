# -------------------------------------------
# IMPORTS
# -------------------------------------------
from flask import Flask, request, jsonify, send_from_directory, render_template, session
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os
import random
import difflib

# -------------------------------------------
# CLOUDINARY CONFIGURATION
# -------------------------------------------
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# -------------------------------------------
# FLASK APP SETUP
# -------------------------------------------
app = Flask(__name__, static_folder='.', template_folder='templates')
CORS(app)

# Secret key for session handling (required for storing user balance & transactions)
app.secret_key = 'myscrete123'

# -------------------------------------------
# SIMPLE AI FUNCTION
# -------------------------------------------
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

# -------------------------------------------
# ROUTES
# -------------------------------------------

# Default route → Chat interface
@app.route('/')
def home():
    return render_template('chat.html')


# Chat API endpoint for processing messages
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if data and 'message' in data:
        user_input = data.get('message', '')
        reply = chat_ai(user_input)
        return jsonify({'reply': reply})
    return jsonify({'reply': "Send a message."})


# -------------------------------------------
# CAMPUS MANAGER (BUDGET LOGGING FEATURE)
# -------------------------------------------
@app.route('/campus', methods=['GET', 'POST'])
def campus():
    # On first visit, initialize budget and empty transaction list
    if 'balance' not in session:
        session['balance'] = 50000  # Starting budget projection
        session['transactions'] = []

    # Handle form submission
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        amount = float(request.form.get('amount', 0))

        # Reduce budget based on user input
        session['balance'] -= amount

        # Store transaction
        session['transactions'].append({
            'description': description,
            'amount': amount
        })

    # Render page with current data
    return render_template(
        'campus.html',
        transactions=session.get('transactions', []),
        balance=session.get('balance', 50000)
    )


# -------------------------------------------
# STATIC FILE SERVING (OPTIONAL)
# -------------------------------------------
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)


# -------------------------------------------
# RUN APP LOCALLY
# -------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
