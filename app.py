from flask import Flask, render_template, session, redirect, send_from_directory
from config import Config
from routes.auth_routes import auth
from routes.patent_routes import patent
from dotenv import load_dotenv
import webbrowser
import threading
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app.register_blueprint(auth)
app.register_blueprint(patent)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    os.makedirs("uploads/diagrams", exist_ok=True)
    threading.Timer(1, open_browser).start()
    app.run(debug=True)