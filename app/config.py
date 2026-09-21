"""
Configuration module for Flask application.
Loads environment variables using python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    # For Vercel/serverless environments, use /tmp for SQLite
    if os.environ.get('VERCEL') or DATABASE_URL.startswith('sqlite:///'):
        if not DATABASE_URL.startswith('sqlite:////tmp'):
            DATABASE_URL = DATABASE_URL.replace('sqlite:///', 'sqlite:////tmp/')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def validate_config():
        """Validate that all required environment variables are set."""
        required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
