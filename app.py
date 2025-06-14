from flask import Flask, render_template, request
import google.generativeai as genai
import os
import langdetect  # for detecting input language

app = Flask(__name__)

# Configure your Gemini API key
API_KEY = "AIzaSyA_84rmTgnFdvzjpFdB8p3xYoziCVbcEic"
genai.configure(api_key=API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""

    if request.method == "POST":
        user_input = request.form["message"].strip()
        mode = request.form.get("mode", "general")

        if not user_input:
            response_text = "Kumba AI was created by Tawanda Muzangazi to offer personalized assistance for Zimbabweans."
        else:
            try:
                detected_lang = langdetect.detect(user_input)
            except:
                detected_lang = "en"

            language_instruction = f"\nPlease respond in the same language detected: {detected_lang}." if detected_lang != "en" else ""

            if mode == "study":
                prompt = f"""
Please answer the following question clearly and professionally:

**{user_input}**

- Use headings and bullet points
- Highlight important concepts in bold
- If it's a history topic, include examples and short study tips
- Format the response as HTML so it displays well on a web page
- Use a bold heading for each country or topic
- Use <ul> and <li> for bullet points
- Keep spacing clean and readable
- Do NOT wrap the entire thing in triple backticks
- Return only valid HTML to be rendered inside a webpage
{language_instruction}
"""
            elif mode == "news":
                prompt = f"""
Summarize today’s top news in Africa in a clear, professional format:

- Use a bold heading for each country or topic
- Use <ul> and <li> for bullet points
- Keep spacing clean and readable
- Do NOT wrap the entire thing in triple backticks
- Return only valid HTML
{language_instruction}
"""
            elif mode == "motivation":
                prompt = f"Give an uplifting motivational quote and a short study tip.{language_instruction}"
            elif mode == "fun":
                prompt = f"Tell a clean, funny joke or riddle.{language_instruction}"
            elif mode == "planner":
                prompt = f"Suggest a study or productivity plan based on this request: {user_input}.{language_instruction}"
            elif mode == "language":
                prompt = f"Translate this into simple French and explain each word: {user_input}"
            elif mode == "story":
                prompt = f"Write a complete short story based on this prompt: {user_input}.{language_instruction}"
            else:
                prompt = f"{user_input}{language_instruction}"

            response = chat.send_message(prompt)
            response_text = response.text.strip()

            if response_text.startswith("```html"):
                response_text = response_text.replace("```html", "").replace("```", "")
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "")

    return render_template("index.html", response=response_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
