from flask import Flask, Response, request, jsonify
import requests
import json
from flask_cors import CORS
import torch
from diffusers import MotionAdapter, AnimateDiffPipeline, DDIMScheduler
from PIL import Image
import io
import imageio
import numpy as np
import logging
import os

app = Flask(__name__)
CORS(app)

NEGATIVE_PROMPTS = {
    "product_shoes": "blurry, text, watermark, distorted legs, logo",
    "product_clothes": "low resolution, logo, text, messy background",
    "default": "text, blur, watermark, ugly, distorted",
}

OLLAMA_URL = "http://localhost:11434/api/generate"
IMAGE_GEN_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load video generation models at startup
adapter = MotionAdapter.from_pretrained(
    "guoyww/animatediff-motion-adapter-v1-5-2",
    torch_dtype=torch.float16
)
pipe = AnimateDiffPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    motion_adapter=adapter, 
    torch_dtype=torch.float16
).to("cuda")
pipe.scheduler = DDIMScheduler.from_pretrained(
    "runwayml/stable-diffusion-v1-5", subfolder="scheduler",
    clip_sample=False, timestep_spacing="linspace"
)

#pipe.enable_xformers_memory_efficient_attention()

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
    step = data.get("step", "")

    try:
        if step == "negative":
            prompt = get_negative_prompt("default")
            return jsonify({"status": "generating_negative", "negative": prompt})
        elif step == "image":
            prompt = data.get("prompt_text", "")
            negative = data.get("negative_prompt", "")
            image, image_prompt = generate_image(prompt, negative)  # Return both image and prompt
            return jsonify({"status": "generating_image", "image": image, "image_prompt": image_prompt})
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
    generated_prompt = response.json()["response"].strip()
    print(f"Generated prompt from llama3: {generated_prompt}")
    return generated_prompt

def get_negative_prompt(context_type="default"):
    return NEGATIVE_PROMPTS.get(context_type, NEGATIVE_PROMPTS["default"])

def generate_image(prompt, negative_prompt=""):
    image_prompt = generate_image_prompt(prompt)
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
    image = res.json()["images"][0]
    return image, image_prompt  # Return both image and the specific prompt

@app.route("/generate_video", methods=["POST"])
def generate_video():
    try:
        logger.debug("Received request to /generate_video")
        
        # Get image and prompt from FormData
        image_data = request.files["image"].read()
        prompt = request.form.get("prompt", "A vibrant animated scene")  # Will use specific image_prompt
        logger.debug(f"Prompt: {prompt}")
        
        # Load and preprocess image
        logger.debug("Loading and resizing image")
        init_img = Image.open(io.BytesIO(image_data)).convert("RGB")
        init_img = init_img.resize((512, 512))
        logger.debug(f"Image size: {init_img.size}")
        
        # Video generation parameters
        frames = 16
        fps = 8
        seed = 42
        
        # Set random seed
        logger.debug("Setting random seed")
        generator = torch.Generator(device="cuda").manual_seed(seed)
        
        # Generate video frames
        logger.debug("Generating video frames with AnimateDiffPipeline")
        result = pipe(
            prompt=prompt,
            init_image=init_img,
            num_inference_steps=20,  # Optionally increase to 50
            generator=generator,
            num_frames=frames,
            guidance_scale=7.5  # Optionally increase to 10.0
        )
        video_frames = result.frames[0]
        logger.debug(f"Generated {len(video_frames)} frames")
        
        # Save video to buffer and file
        logger.debug("Encoding video")
        buf = io.BytesIO()
        writer = imageio.get_writer(
            buf, format="mp4", mode="I", fps=fps, codec="libx264"
        )
        output_path = os.path.join(os.getcwd(), "generated_video.mp4")
        file_writer = imageio.get_writer(
            output_path, format="mp4", mode="I", fps=fps, codec="libx264"
        )
        
        for i, frame in enumerate(video_frames):
            logger.debug(f"Processing frame {i}: type={type(frame)}")
            frame_np = np.array(frame)
            frame_np = (frame_np * 255).astype(np.uint8)
            writer.append_data(frame_np)
            file_writer.append_data(frame_np)
        
        writer.close()
        file_writer.close()
        buf.seek(0)
        logger.debug(f"Video saved to {output_path}")
        
        return Response(buf.getvalue(), mimetype="video/mp4")
    
    except Exception as e:
        logger.error(f"Error in generate_video: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)