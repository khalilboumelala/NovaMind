from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import MySQLdb
from flask_mysqldb import MySQL
from flask_cors import CORS
import requests
import json
from functools import wraps
import pymysql
import os
import time


'''
app = Flask(__name__)
app.config.from_pyfile('config.py')
print("MYSQL_HOST:", app.config.get('MYSQL_HOST'))
print("MYSQL_DB:  ", app.config.get('MYSQL_DB'))
mysql = MySQL()             # no app yet
app.config.from_pyfile('config.py')
mysql.init_app(app)         # bind after config


CORS(app)

db_config = {
    'host':     app.config['MYSQL_HOST'],
    'user':     app.config['MYSQL_USER'],
    'password': app.config['MYSQL_PASSWORD'],
    'db':       app.config['MYSQL_DB'],
   # 'port':     app.config.get('MYSQL_PORT', 3306)
}
conn = pymysql.connect(**db_config)
cur = conn.cursor()
'''


# Debug environment variables
print("Environment variables:", os.environ)

app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')
print("Config after loading:", app.config)

# Manually set config if not loaded
# Manually set config if not loaded
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'mysql')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'rootroot')  # Explicitly set to empty string
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'novamind')
mysql = MySQL()
mysql.init_app(app)


db_config = {
    'host': app.config['MYSQL_HOST'],
    'user': app.config['MYSQL_USER'],
    'password': app.config['MYSQL_PASSWORD'],
    'db': app.config['MYSQL_DB'],
}

print("db_config:", db_config)
# Add retry logic for database connection
max_retries = 5
retry_interval = 5  # seconds
for attempt in range(max_retries):
    try:
        conn = pymysql.connect(**db_config)
        cur = conn.cursor()
        print("Connected to MySQL!", conn)
        break
    except pymysql.err.OperationalError as e:
        if attempt < max_retries - 1:
            print(f"Failed to connect to MySQL: {e}. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
        else:
            print(f"Failed to connect to MySQL after {max_retries} attempts: {e}")
            raise

print("Connected!", conn)

# Backend settings

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
        cur = conn.cursor()
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
        cur = conn.cursor()
        cur.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, pwd))
        conn.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

# ===== Routes Gestion Chatbot =====

@app.route('/start_conversation', methods=['POST','GET'])
@login_required
def start_conversation():
    user_id = get_current_user_id()

    # Try to get message safely
    user_input = request.form.get('message', None)

    title = "New Conversation"
    
    cur = conn.cursor()
    cur.execute("INSERT INTO conversation_threads (user_id, title) VALUES (%s, %s)", (user_id, title))
    conn.commit()
    thread_id = cur.lastrowid

    # Only insert a message if there is one
    if user_input:
        cur.execute("INSERT INTO messages (thread_id, user_id, role, message) VALUES (%s, %s, %s, %s)", 
                    (thread_id, user_id, 'user', user_input))
        mysql.connection.commit()

    cur.close()
    print("Redirecting to chatbotintegration with thread_id:", thread_id)

    return redirect(url_for('chatbotintegration', thread_id=thread_id))


@app.route('/send_message/<int:thread_id>', methods=['POST'])
@login_required
def send_message(thread_id):
    user_input = request.form['message']
    user_id = get_current_user_id()

    cur = conn.cursor()
    cur.execute("INSERT INTO messages (thread_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
                (thread_id, user_id, 'user', user_input))
    conn.commit()
    cur.close()

    return redirect(url_for('chatbotintegration', thread_id=thread_id))


@app.route('/chatbotintegration', defaults={'thread_id': None})
@app.route('/chatbotintegration/<int:thread_id>')
@login_required
def chatbotintegration(thread_id=None):
    user_id = get_current_user_id()

    cur = conn.cursor()
    cur.execute("SELECT id, title FROM conversation_threads WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    threads = cur.fetchall()

    messages = []
    if thread_id:
        cur.execute("SELECT role, message FROM messages WHERE thread_id = %s ORDER BY created_at ASC", (thread_id,))
        messages = cur.fetchall()
    
    cur.close()

    return render_template('chatbotintegration.html', username=session['username'], threads=threads, messages=messages, thread_id=thread_id)



@app.route('/chatbot', defaults={'thread_id': None})
@app.route('/chatbot/<int:thread_id>')
@login_required
def chatbot(thread_id=None):
    user_id = get_current_user_id()

    cur = conn.cursor()
    cur.execute("SELECT id, title FROM conversation_threads WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    threads = cur.fetchall()

    messages = []
    if thread_id:
        cur.execute("SELECT role, message FROM messages WHERE thread_id = %s ORDER BY created_at ASC", (thread_id,))
        messages = cur.fetchall()
    
    cur.close()

    return render_template('chatbot.html', username=session['username'], threads=threads, messages=messages, thread_id=thread_id)


@app.route('/chatbotguest')
@login_required
def chatbotguest(thread_id=None):
    return render_template('chatbotinterface.html')

# ===== Backend Streaming Texte & Génération Image =====

# ===== Lancement App =====

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(host='0.0.0.0', port=5000, debug=True)