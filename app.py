from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
import requests
import json
from functools import wraps

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)
CORS(app)

# Backend settings
OLLAMA_URL = "http://localhost:11434/api/generate"
IMAGE_GEN_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
NEGATIVE_PROMPTS = {
    "product_shoes": "blurry, text, watermark, distorted legs, logo",
    "product_clothes": "low resolution, logo, text, messy background",
    "default": "text, blur, watermark, ugly, distorted",
}

# ===== Fonctions Utilitaires =====

def is_logged_in():
    return 'username' in session

def get_current_user_id():
    return session.get('user_id')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_conversation_title(user_input):
    words = user_input.strip().split()[:10]
    return ' '.join(words) if words else "Nouvelle Conversation"

# ===== Routes Pages de Base =====

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
@login_required
def home():
    return render_template('home.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, password FROM user WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[2]:
            session['user_id'] = user[0]
            session['username'] = user[1]
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
    session.pop('user_id', None)
    return redirect(url_for('login'))

# ===== Routes Gestion Chatbot =====

@app.route('/start_conversation', methods=['POST'])
@login_required
def start_conversation():
    user_id = get_current_user_id()

    # Try to get message safely
    user_input = request.form.get('message', None)

    title = "New Conversation"
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO conversation_threads (user_id, title) VALUES (%s, %s)", (user_id, title))
    mysql.connection.commit()
    thread_id = cur.lastrowid

    # Only insert a message if there is one
    if user_input:
        cur.execute("INSERT INTO messages (thread_id, user_id, role, message) VALUES (%s, %s, %s, %s)", 
                    (thread_id, user_id, 'user', user_input))
        mysql.connection.commit()

    cur.close()

    return redirect(url_for('chatbot', thread_id=thread_id))


@app.route('/send_message/<int:thread_id>', methods=['POST'])
@login_required
def send_message(thread_id):
    user_input = request.form['message']
    user_id = get_current_user_id()

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (thread_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
                (thread_id, user_id, 'user', user_input))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('chatbot', thread_id=thread_id))

@app.route('/chatbot', defaults={'thread_id': None})
@app.route('/chatbot/<int:thread_id>')
@login_required
def chatbot(thread_id):
    user_id = get_current_user_id()

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM conversation_threads WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    threads = cur.fetchall()

    messages = []
    if thread_id:
        cur.execute("SELECT role, message FROM messages WHERE thread_id = %s ORDER BY created_at ASC", (thread_id,))
        messages = cur.fetchall()
    
    cur.close()

    return render_template('chatbot.html', username=session['username'], threads=threads, messages=messages, thread_id=thread_id)

# ===== Backend Streaming Texte & Génération Image =====

@app.route('/stream_text')
@login_required
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
@login_required
def generate_step():
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

# ===== Lancement App =====

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)