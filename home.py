from flask import Flask, render_template, request
import google.generativeai as genai
import pytesseract
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from PIL import Image
import io
import fitz  # PyMuPDF

app = Flask(__name__)

# Configure Gemini
API_KEY = "AIzaSyA_84rmTgnFdvzjpFdB8p3xYoziCVbcEic"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-pro")
chat = model.start_chat()

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_image(image_file):
    image = Image.open(image_file.stream)
    return pytesseract.image_to_string(image)

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    if request.method == "POST":
        user_input = request.form.get("message")
        uploaded_file = request.files.get("file")

        input_text = ""

        if user_input:
            input_text = user_input
        elif uploaded_file:
            if uploaded_file.filename.endswith(".pdf"):
                input_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.filename.endswith((".png", ".jpg", ".jpeg")):
                input_text = extract_text_from_image(uploaded_file)

        if input_text:
            prompt = f"""
You are a tutor for ZIMSEC students. Use clear structure, **bold headings**, bullets, and examples.

**Question/Content:**
{input_text}
"""
            response = chat.send_message(prompt)
            response_text = response.text

    return render_template("home.html", response=response_text)

if __name__ == "__main__":
    app.run(debug=True)
