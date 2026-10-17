import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'carebridge-secure-key-elderly-health-2026')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'carebridge.db'))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}
    
    # AI API Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', os.environ.get('AI_API_KEY', ''))
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    AI_MODEL = os.environ.get('AI_MODEL', 'local-demo')
    
    # OCR Settings
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD', '')
