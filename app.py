from flask import Flask, render_template, request
import google.generativeai as genai

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
        user_input = request.form["message"]

        # Modified prompt to encourage better formatting
        prompt = f"""
Please answer the following question clearly and professionally:

**{user_input}**

- Use headings and bullet points
- Highlight important concepts in bold
- If it's a history topic, include examples and short study tips
- Format the response as HTML so it displays well on a web page
"""

        response = chat.send_message(prompt)
        response_text = response.text

    return render_template("index.html", response=response_text)

if __name__ == "__main__":
    app.run(debug=True)
