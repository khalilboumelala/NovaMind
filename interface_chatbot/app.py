from flask import Flask, request, jsonify
import requests
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
IMAGE_GEN_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

def generate_text(user_input):
    payload = {
        "model": "llama3",
        "prompt": f"Generate a social media marketing text for: {user_input}",
        "stream": False
    }
    res = requests.post(OLLAMA_URL, json=payload)
    return res.json()["response"].strip()

def generate_negative_prompt(user_input):
    prompt = f"Given this social media topic: '{user_input}', generate a negative prompt for image generation to avoid bad results (e.g., blur, low quality, distorted face)."
    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"].strip()

def generate_image(prompt, negative_prompt=""):
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 20,
        "cfg_scale": 7,
        "width": 512,
        "height": 512,
        "seed": -1
    }
    res = requests.post(IMAGE_GEN_URL, json=payload)
    return res.json()["images"][0]

@app.route("/generate_step", methods=["POST"])
def generate_step():
    data = request.get_json()
    user_input = data.get("prompt", "")
    step = data.get("step", "")

    try:
        if step == "text":
            return jsonify({"status": "generating_text", "text": generate_text(user_input)})
        elif step == "negative":
            return jsonify({"status": "generating_negative", "negative": generate_negative_prompt(user_input)})
        elif step == "image":
            prompt = data.get("prompt_text", "")
            negative = data.get("negative_prompt", "")
            return jsonify({"status": "generating_image", "image": generate_image(prompt, negative)})
        else:
            return jsonify({"error": "Invalid step"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
