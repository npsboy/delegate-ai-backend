from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv() #loads the environment variables from .env file
client = OpenAI()
app = Flask(__name__) #_name_ tells flask that it is the main module

@app.route("/")
def home():
    return "DelegateAI backend is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"response": reply})
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)