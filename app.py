from flask import Flask, render_template, request, send_file
import google.generativeai as genai
import os
import langdetect
import re
import fitz  # PyMuPDF for PDF text extraction
from xhtml2pdf import pisa
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
API_KEY = "AIzaSyA_84rmTgnFdvzjpFdB8p3xYoziCVbcEic"
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
ALLOWED_EXTENSIONS = {"pdf", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Gemini setup
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

# Utilities
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_path):
    if file_path.lower().endswith(".pdf"):
        doc = fitz.open(file_path)
        return "\n".join(page.get_text() for page in doc)
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def clean_response(text):
    text = re.sub(r"```(?:html)?", "", text)
    text = re.sub(r"^(Okay,|Sure,)?\s*(here('s| is))?[^<\n]*<", "<", text, flags=re.IGNORECASE)
    text = re.sub(r"(Let me know.*|Hope this helps.*|I'm here if you need.*)$", "", text, flags=re.IGNORECASE).strip()
    return text

def generate_pdf(html_text, output_path):
    with open(output_path, "w+b") as f:
        pisa.CreatePDF(html_text, dest=f)

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    uploaded_text = ""

    if request.method == "POST":
        user_input = request.form.get("message", "").strip()
        mode = request.form.get("mode", "general")

        # Handle uploaded file
        file = request.files.get("document")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            uploaded_text = extract_text(filepath)

        if not user_input and not uploaded_text:
            response_text = "<h2>Kumba AI created by Tawanda Muzangazi</h2><p>Welcome! Ask me anything or choose a tool from the menu.</p>"
        else:
            try:
                detected_lang = langdetect.detect(user_input or uploaded_text)
            except:
                detected_lang = "en"

            language_instruction = (
                f"\nRespond in the same language detected: {detected_lang}."
                if detected_lang != "en"
                else ""
            )

            base_text = f"\nDOCUMENT:\n{uploaded_text}\n\nQUESTION:\n{user_input}" if uploaded_text else user_input

            if mode == "study":
                prompt = f"""
Please answer the following clearly and professionally:

{base_text}

- Use headings and bullet points
- Use bold for important terms
- Use <ul> and <li> for lists
- Format the response as clean HTML (no triple backticks)
{language_instruction}
"""
            else:
                prompt = f"""
Please write a friendly, helpful answer to this:

{base_text}

- Use headings, paragraphs, and clean HTML
- Do NOT include any phrases like "Here's your answer"
- Do NOT use triple backticks
- Avoid signing off with "I hope this helps" or similar
{language_instruction}
"""

            response = chat.send_message(prompt)
            response_text = clean_response(response.text)

    else:
        response_text = "<h2>Kumba AI created by Tawanda Muzangazi</h2><p>Welcome! Ask me anything or choose a tool from the menu.</p>"

    return render_template("index.html", response=response_text)

@app.route("/download", methods=["POST"])
def download():
    html_content = request.form.get("html", "")
    output_path = os.path.join(DOWNLOAD_FOLDER, "response.pdf")
    generate_pdf(html_content, output_path)
    return send_file(output_path, as_attachment=True)

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
