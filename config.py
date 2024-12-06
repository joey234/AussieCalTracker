import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///aussiecal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # Default 16MB
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Gemini API settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Food database
    BASE_DIR = Path(__file__).resolve().parent
    FOOD_DB_PATH = BASE_DIR / 'app' / 'services' / 'data' / 'aus_food_db.csv'
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Create upload folder if it doesn't exist
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # Validate required environment variables
        required_vars = ['SECRET_KEY', 'GOOGLE_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")