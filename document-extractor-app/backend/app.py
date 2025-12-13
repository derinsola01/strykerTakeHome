
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HF_TOKEN = os.getenv("HF_API_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query(payload):
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    return response.json()

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    text = file.read().decode("utf-8")

    prompt = f"Extract key invoice details like vendor, date, total amount:\n{text}"
    result = query({"inputs": prompt})

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
