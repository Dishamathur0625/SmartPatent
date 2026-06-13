import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "smartpatent_secret_key")

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "smartpatent")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LENS_API_KEY = os.getenv("LENS_API_KEY")

    UPLOAD_DIAGRAM_FOLDER = "uploads/diagrams"