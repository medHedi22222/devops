"""
Vercel Python API entry point.
This imports the existing Flask app for Vercel deployment.
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the existing Flask app
from app import create_app

# Create the Flask application
app = create_app()

# For Vercel deployment, use /tmp for database if needed
if os.environ.get('VERCEL'):
    os.environ['DATABASE_URL'] = 'sqlite:////tmp/app.db'

# Vercel will automatically detect the 'app' variable in api/index.py
