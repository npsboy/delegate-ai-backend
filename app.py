from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
from flask_cors import CORS
import requests
import time

load_dotenv() #loads the environment variables from .env file
client = OpenAI()
app = Flask(__name__) #_name_ tells flask that it is the main module
CORS(app) # Enable CORS for all routes


HUMANIZEAI_API_KEY = os.getenv("HUMANIZEAI_API_KEY")
HumanizeAI_url = "https://api.humanizeai.pro/v1"

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
            model="o4-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/humanize", methods=["POST"])
def humanize():
    data = request.get_json()
    text = data.get("text")

    if not text or len(text.split()) < 30:
        return jsonify({"error": "Text must have more than 30 words"}), 400

    headers = {
        "x-api-key": HUMANIZEAI_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Submit text
        post_response = requests.post(HumanizeAI_url, json={"text": text}, headers=headers)

        try:
            task_data = post_response.json()
        except ValueError:
            return jsonify({
                "error": "Failed to parse JSON from Humanizer API (POST response)",
                "status_code": post_response.status_code,
                "raw": post_response.text
            }), 500

        task_id = task_data.get("id")
        if not task_id:
            return jsonify({"error": "No task ID returned", "details": task_data}), 500

        # Step 2: Poll for result
        max_wait_time = 5  # seconds
        poll_interval = 1  # seconds
        waited = 0

        while waited < max_wait_time:
            result_response = requests.get(HumanizeAI_url, headers=headers, params={"id": task_id})

            try:
                result_data = result_response.json()
            except ValueError:
                return jsonify({
                    "error": "Failed to parse JSON from Humanizer API (GET result)",
                    "status_code": result_response.status_code,
                    "raw": result_response.text
                }), 500

            if result_data.get("status") == "done":
                return jsonify({
                    "original": result_data.get("original"),
                    "humanized": result_data.get("humanized")
                })

            elif result_data.get("status") == "failed":
                return jsonify({"error": "Processing failed", "details": result_data}), 500

            time.sleep(poll_interval)
            waited += poll_interval

        # Timed out
        return jsonify({
            "status": "processing",
            "message": "Still processing, try again later",
            "task_id": task_id
        }), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)