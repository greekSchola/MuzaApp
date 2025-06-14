from flask import Flask, render_template, request
import google.generativeai as genai
import os
import langdetect
import re

app = Flask(__name__)

# Gemini API Key
API_KEY = "AIzaSyA_84rmTgnFdvzjpFdB8p3xYoziCVbcEic"
genai.configure(api_key=API_KEY)

# Load the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""

    if request.method == "POST":
        user_input = request.form["message"].strip()
        mode = request.form.get("mode", "general")

        if not user_input:
            response_text = "<h2>Kumba AI created by Tawanda Muzangazi</h2><p>Welcome! Ask me anything or choose a tool from the menu.</p>"
        else:
            try:
                detected_lang = langdetect.detect(user_input)
            except:
                detected_lang = "en"

            language_instruction = (
                f"\nRespond in the same language detected: {detected_lang}."
                if detected_lang != "en"
                else ""
            )

            if mode == "study":
                prompt = f"""
Please answer the following clearly and professionally:

{user_input}

- Use headings and bullet points
- Use bold for important terms
- Use <ul> and <li> for lists
- Format the response as clean HTML (no triple backticks)
{language_instruction}
"""
            else:  # General mode
                prompt = f"""
Please write a friendly, helpful answer to this:

{user_input}

- Use headings, paragraphs, and clean HTML
- Do NOT include any phrases like "Here's your answer"
- Do NOT use triple backticks
- Avoid signing off with "I hope this helps" or similar
{language_instruction}
"""

            response = chat.send_message(prompt)
            response_text = clean_response(response.text)

    else:
        # GET request shows landing message
        response_text = "<h2>Kumba AI created by Tawanda Muzangazi</h2><p>Welcome! Ask me anything or choose a tool from the menu.</p>"

    return render_template("index.html", response=response_text)


def clean_response(text):
    """Remove boilerplate phrases and code fences from model output."""
    # Remove triple backticks
    text = re.sub(r"```(?:html)?", "", text)
    
    # Remove leading phrases like "Here's an answer..."
    text = re.sub(r"^(Okay,|Sure,)?\s*(here('s| is))?[^<\n]*<", "<", text, flags=re.IGNORECASE)
    
    # Remove polite closing lines
    text = re.sub(r"(Let me know.*|Hope this helps.*|I'm here if you need.*)$", "", text, flags=re.IGNORECASE).strip()
    
    return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
