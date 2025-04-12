from flask import Flask, Response, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

NEGATIVE_PROMPTS = {
    "product_shoes": "blurry, text, watermark, distorted legs, logo",
    "product_clothes": "low resolution, logo, text, messy background",
    "default": "text, blur, watermark, ugly, distorted",
}


OLLAMA_URL = "http://localhost:11434/api/generate"
IMAGE_GEN_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"


@app.route('/stream_text')
def stream_text():
    user_input = request.args.get("prompt", "")

    def generate():
        prompt = (
    f"You are a social media expert. Create a well-formatted Markdown post for the idea:\n"
    f"{user_input}\n\n"
    f"✅ Format it with Markdown.\n"
    f"✅ Add a line break after every heading or bold title.\n"
    f"✅ Put each feature (bullet) on its own line using '-', '*', or '•'.\n"
    f"✅ Add empty lines between major sections.\n"
    f"✅ Do NOT place text directly after bold titles without a break.\n"
    f"✅ Hashtags should appear in their own line at the end."
)

        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": True
        }
        with requests.post(OLLAMA_URL, json=payload, stream=True) as r:
            for line in r.iter_lines(decode_unicode=True):
                if line.strip():  # skip empty lines
                    try:
                        line_data = json.loads(line)
                        token = line_data.get("response", "")
                        yield f"data: {token}\n\n"
                    except Exception as e:
                        print("⚠️ JSON decode error:", e)
            yield "data: [DONE]\n\n"

    return Response(generate(), content_type='text/event-stream')

@app.route("/generate_step", methods=["POST"])
def generate_step():
    data = request.get_json()
    user_input = data.get("prompt", "")
    step = data.get("step", "")

    try:
        if step == "negative":
            prompt = get_negative_prompt("default")#f"Given this social media topic: '{user_input}', generate a negative prompt for image generation to avoid bad results (e.g., blur, low quality, distorted face)."
            #response = requests.post(OLLAMA_URL, json={
            #    "model": "llama3",
            #    "prompt": prompt,
            #    "stream": False
            #})
            #return jsonify({"status": "generating_negative", "negative": response.json()["response"].strip()})
            return jsonify({"status": "generating_negative", "negative": prompt})
            
        elif step == "image":
            prompt = data.get("prompt_text", "")
            negative = data.get("negative_prompt", "")
            image = generate_image(prompt, negative)
            return jsonify({"status": "generating_image", "image": image})
        else:
            return jsonify({"error": "Invalid step"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
def generate_image_prompt(user_input):
    prompt = (
        f"Based on this marketing idea:\n\n"
        f"{user_input}\n\n"
        f"Generate a short, vivid image generation prompt suitable for a text-to-image model. "
        f"Describe what the image should show, avoiding any textual or caption elements."
    )
    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"].strip()


def get_negative_prompt(context_type="default"):
    return NEGATIVE_PROMPTS.get(context_type, NEGATIVE_PROMPTS["default"])

def generate_image(prompt, negative_prompt=""):
    # Add more detailed negative cues to avoid text on image
    image_prompt= generate_image_prompt(prompt)
    full_negative = negative_prompt + ", text, watermark, label, caption, subtitles, logo, words"

    payload = {
        "prompt": image_prompt,
        "negative_prompt": full_negative,
        "steps": 20,
        "cfg_scale": 7,
        "width": 512,
        "height": 512,
        "seed": -1
    }
    res = requests.post(IMAGE_GEN_URL, json=payload)
    return res.json()["images"][0]

if __name__ == "__main__":
    app.run(port=5000)
