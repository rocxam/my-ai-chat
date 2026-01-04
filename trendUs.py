# -------------------------------------------
# IMPORTS
# -------------------------------------------
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from supabase import create_client, Client
import cloudinary
import cloudinary.uploader
import google.generativeai as genai
import os
import random
import difflib
import json
import time

# -------------------------------------------
# CONFIGURATION (AI & DATABASE)
# -------------------------------------------

# 1. Gemini AI Config
GEMINI_KEY = "AIzaSyB2F71wQjvNCwRC8qt29w8I_rbNH6FlGms"
genai.configure(api_key=GEMINI_KEY)

# 2. Supabase Config
SUPABASE_URL = "https://hbszddxerbbvteeqnagf.supabase.co"
SUPABASE_KEY = "sb_publishable_T0Iy6AWAP_YZu-TG6C4Dbw_I0uK-H3z" 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Cloudinary Config (Make sure these are set in Render Environment Variables)
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# -------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------

def scan_invoice(file_path):
    """Uses Gemini Vision to extract data from the PDF with a processing wait loop."""
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # 1. Upload to Gemini's temp storage
    sample_file = genai.upload_file(path=file_path, display_name="Invoice")

    # 2. WAIT loop: Prevents hanging if the file isn't ready immediately
    while sample_file.state.name == "PROCESSING":
        time.sleep(2)
        sample_file = genai.get_file(sample_file.name)

    if sample_file.state.name == "FAILED":
        raise Exception("Gemini file processing failed.")

    prompt = """
    Analyze this document as an expert accountant.
    Extract:
    1. 'date': Invoice date.
    2. 'client company': Name of company being supplied.
    3. 'amount': Total numerical value.
    4. 'summary': 1-sentence description of goods/services.
    
    Return ONLY a JSON object.
    """

    # 3. Generate content
    response = model.generate_content([prompt, sample_file])
    
    # 4. Clean AI response to ensure it is pure JSON
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def chat_ai(user_input):
    """Handles the greeting logic and AI chat responses"""
    text = user_input.strip().lower()
    greetings = ["hi", "hello", "hey", "sup", "howdy"]
    replies = ["Wagwan 😊", "Sup 😊", "Hey! How’s your day going?"]
    
    match = difflib.get_close_matches(text, greetings, n=1, cutoff=0.5)
    if match:
        return random.choice(replies)
    return "Kinaye-bloodii 👋"

# -------------------------------------------
# FLASK APP SETUP
# -------------------------------------------
app = Flask(__name__, static_folder='.', template_folder='templates')
CORS(app)

# -------------------------------------------
# ROUTES
# -------------------------------------------

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if data and 'message' in data:
        reply = chat_ai(data.get('message', ''))
        return jsonify({'reply': reply})
    return jsonify({'reply': "Send a message."})

@app.route('/upload', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
        
    file = request.files['file']
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)

    try:
        # 1. AI Scan (Gemini)
        scanned_data = scan_invoice(temp_path)

        # 2. Cloudinary Upload
        upload_result = cloudinary.uploader.upload(temp_path, resource_type="auto")
        pdf_link = upload_result.get('secure_url')

        # 3. Save to Supabase
        supabase.table("invoice summary").insert({
            "date": scanned_data.get("date"),
            "client company": scanned_data.get("client company"),
            "amount": scanned_data.get("amount"),
            "summary": scanned_data.get("summary"),
            "pdf_url": pdf_link,
            "status": "Unpaid" 
        }).execute()

        # Clean up local file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({"message": "Invoice scanned and added to portal!"})
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e)}), 500

@app.route('/get-invoices')
def get_invoices():
    # Pulls the latest 10 invoices
    response = supabase.table("invoice summary").select("*").order('date', desc=True).limit(10).execute()
    return jsonify(response.data)

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

# -------------------------------------------
# RUN APP
# -------------------------------------------
if __name__ == '__main__':
    # Using environment port for Render deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)