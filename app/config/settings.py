import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'expenseiq-secret-key-2024-change-in-production-xyz')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'expenseiq-jwt-secret-key-2024-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    MONGODB_URI = os.environ.get('MONGO_URI', '') or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/expenseiq')
    DB_NAME = os.environ.get('DB_NAME', 'expenseiq')
    
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    FAST2SMS_API_KEY = os.environ.get('FAST2SMS_API_KEY', '')
    MSG91_AUTH_KEY = os.environ.get('MSG91_AUTH_KEY', '')
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'csv', 'xlsx'}
    
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    PORT = int(os.environ.get('PORT', 5000))
    
    CURRENCY_SYMBOL = '₹'
    CURRENCY_CODE = 'INR'
    COUNTRY = 'India'
