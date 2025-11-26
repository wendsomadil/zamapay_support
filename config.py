# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAzUKy-4XE7svSulN1IksyFeHrdVQpQqLw")

# Configuration de l'application
APP_NAME = "ZamaPay"
VERSION = "2.0"
