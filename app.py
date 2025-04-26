from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
import time
import requests
import json

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)
CORS(app)

# Utilisation du backend chatbot existant
def login_required():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

# === ROUTES UTILISATEUR ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home2')
def index2():
    return render_template('index-2.html')

@app.route('/home3')
def index3():
    return render_template('index-3.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs')
def blogs():
    return render_template('blog-single.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'user_id' in session:
        # Récupérer ou créer un thread de conversation pour l'utilisateur
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM conversation_threads WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (session['user_id'],))
        thread = cur.fetchone()

        if not thread:
            # Créer un nouveau thread si l'utilisateur n'a pas de thread en cours
            cur.execute("INSERT INTO conversation_threads (user_id) VALUES (%s)", (session['user_id'],))
            mysql.connection.commit()
            cur.execute("SELECT id FROM conversation_threads WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (session['user_id'],))
            thread = cur.fetchone()

        thread_id = thread['id']

        # Récupérer les messages du thread
        cur.execute("SELECT sender, message FROM messages WHERE thread_id = %s ORDER BY created_at", (thread_id,))
        history = cur.fetchall()
        cur.close()

        return render_template('chatbot.html', user_id=session['user_id'], history=history, thread_id=thread_id)
    else:
        return redirect(url_for('login'))


@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' in session:
        message = request.form['message']
        thread_id = request.form['thread_id']

        # Sauvegarder le message dans la base de données
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO messages (thread_id, sender, message) VALUES (%s, %s, %s)", (thread_id, 'user', message))
        mysql.connection.commit()
        cur.close()

        # Rediriger vers le chatbot pour afficher l'historique mis à jour
        return redirect(url_for('chatbot'))
    else:
        return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT username, password FROM user WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['username'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Identifiants invalides')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, pwd))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# === BACKEND CHATBOT EXISTANT ===
OLLAMA_URL = "http://localhost:11434/api/generate"
IMAGE_GEN_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
NEGATIVE_PROMPTS = {
    "product_shoes": "blurry, text, watermark, distorted legs, logo",
    "product_clothes": "low resolution, logo, text, messy background",
    "default": "text, blur, watermark, ugly, distorted",
}

@app.route('/stream_text')
def stream_text():
    auth = login_required()
    if auth: return auth

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
                if line.strip():
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
    auth = login_required()
    if auth: return auth

    data = request.get_json()
    user_input = data.get("prompt", "")
    step = data.get("step", "")

    try:
        if step == "negative":
            prompt = get_negative_prompt("default")
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
    return res.json()["images"][0]

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
