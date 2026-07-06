import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "smartpatent_secret_key")

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "smartpatent")
    MYSQL_POOL_NAME = os.getenv("MYSQL_POOL_NAME", "smartpatent_pool")
    MYSQL_POOL_SIZE = int(os.getenv("MYSQL_POOL_SIZE", "10"))

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LENS_API_KEY = os.getenv("LENS_API_KEY")

    UPLOAD_DIAGRAM_FOLDER = "uploads/diagrams"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB File Upload Limit