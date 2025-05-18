from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    print("✅ '/' endpoint was hit")
    return jsonify({"message": "Hello Railway!"})


