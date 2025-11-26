# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD2mbjiSiPV2PSurmxAUB8MZb9YB02xXNE")

# Configuration de l'application
APP_NAME = "ZamaPay"
VERSION = "2.0"