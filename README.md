
# NovaMind & LLM/Multimodal AI Suite

Welcome to **NovaMind**, a powerful web app suite with two main components:

- A **Flask-based chatbot app** with user authentication and MySQL database integration.  
- A high-end **LLM + Stable Diffusion + AnimateDiff pipeline backend** for text streaming, fine-tuning, image generation, and video generation.

This repository serves as a monorepo or multi-branch project for all these features.

---

## 🚀 Features

### NovaMind Chatbot Web App

- User registration and login with secure session management  
- Interactive chatbot interface with conversation threads  
- Persistent data storage using MySQL  
- Responsive HTML/CSS frontend templates  

### LLM & Multimodal AI Backend

- Streaming text generation from LLaMA 3 model using OLLAMA API  
- Fine-tuning notebooks for LLaMA 3 and Stable Diffusion models (see `notebooks/`)  
- Text-to-image generation using Stable Diffusion API  
- Video generation via AnimateDiff pipeline and MotionAdapter  
- Advanced negative prompt handling for image quality control  
- REST API routes for real-time streaming and multimedia generation  

---

## 🛠️ Technologies Used

- Python 3.9+  
- Flask (Web framework)  
- MySQL (Database for chatbot app)  
- PyMySQL (MySQL connector)  
- Requests (HTTP client)  
- Torch, Diffusers (for Stable Diffusion and AnimateDiff pipelines)  
- PIL (Image processing)  
- ImageIO (Video encoding)  
- Flask-CORS (Cross-Origin Resource Sharing)  

---

## 📦 Prerequisites

- Python 3.9 or higher  
- MySQL Server installed and running (for chatbot app)  
- CUDA-enabled GPU (for AI pipelines)  
- OLLAMA LLaMA 3 local server running on port 11434  
- Stable Diffusion API running locally on port 7860 (e.g. AUTOMATIC1111 web UI)  
- Git and `pip` package manager  

---

## 🔧 Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/NovaMind.git
cd NovaMind
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure MySQL Database (For Chatbot App)

- Ensure MySQL server is running.
- Create a database and user with appropriate permissions.
- Update your Flask app config with database credentials.

### 4. Run Flask Apps

Run the chatbot app (default port 5000):

```bash
export FLASK_APP=chatbot_app.py
flask run
```

Run the LLM & multimodal AI backend (default port 5001):

```bash
python llm_multimodal_app.py
```

---

## 🧪 Usage

- Access the chatbot interface at `http://localhost:5000`
- Use API endpoints of the LLM backend at `http://localhost:5001`

---

## 📂 Notebooks

- `notebooks/llama3_finetune.ipynb` — Fine-tuning LLaMA 3 model  
- `notebooks/stable_diffusion_finetune.ipynb` — Fine-tuning Stable Diffusion model  

---

## 🤝 Contributing

Feel free to submit issues or pull requests. Contributions are welcome!

---

## 📜 License

MIT License


````
