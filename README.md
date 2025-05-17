# NovaMind

Welcome to **NovaMind**, a web-based application built with Flask that provides a chatbot interface, user authentication, and database management using MySQL. This project facilitates interactive conversations and user management, with a focus on ease of setup and scalability.

---

## 🚀 Features

- **User Authentication** – Register and login functionality with session management  
- **Chatbot Integration** – Start and manage conversation threads with a dynamic chatbot interface  
- **Database Management** – Store user data, conversation threads, and messages in a MySQL database  
- **Responsive Design** – HTML templates ensure a user-friendly experience across devices  

---

## 🛠️ Technologies Used

- **Python** – Core programming language  
- **Flask** – Web framework  
- **MySQL** – Relational database for persistent storage  
- **HTML/CSS** – Frontend templates and styling  
- **PyMySQL** – Python library for MySQL connectivity  

---

## 📦 Prerequisites

- Python 3.9 or higher  
- MySQL Server installed and running  
- Git  
- `pip` (Python package manager)  

---

## 🔧 Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/NovaMind.git
cd NovaMind
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, generate it with:

```bash
pip freeze > requirements.txt
```

### 4. Configure MySQL

- Install MySQL Community Server and start the service.  
- Create a database named `novamind`:

```sql
mysql -u root
CREATE DATABASE novamind;
```

- Import schema from `init.sql` (if available):

```sql
USE novamind;
SOURCE path/to/init.sql;
```

Ensure the MySQL root user is configured with an empty password, or update the credentials in `config.py`.

---

### 5. Configure the Application

Update `config.py` with your settings:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'novamind'
SECRET_KEY = 'your_secret_key'  # Or use environment variables
```

---

### 6. Run the Application

```bash
python app.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧑‍💻 Usage

- **Register:** Visit `/register` to create a new user account  
- **Login:** Go to `/login` to access your dashboard  
- **Start Chat:** Navigate to `/start_conversation` to begin  
- **Chatbot:** Use `/chatbotintegration` or `/chatbot` to interact with the chatbot  

---

## 🛠️ MySQL Root with Empty Password (Optional)

If MySQL requires a password but you'd like to use root without one:

1. Stop the MySQL service:

```bash
net stop mysql
```

2. Start MySQL in safe mode:

```bash
mysqld --skip-grant-tables
```

3. Connect and update root credentials:

```sql
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY '';
FLUSH PRIVILEGES;
EXIT;
```

4. Restart MySQL:

```bash
net start mysql
```

---

## 🤝 Contributing

Contributions are welcome!  
Feel free to fork this repository, open issues, or submit pull requests to improve NovaMind.

---

## 📄 License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

## 📝 Notes

- Replace `yourusername` in the clone URL with your GitHub username.  
- Make sure the `LICENSE` file exists and is properly referenced.  
- After committing this README, verify that it displays correctly on GitHub.
