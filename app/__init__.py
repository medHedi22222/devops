"""
Flask application factory pattern.
"""

import os
from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from .models import db
from .auth import auth_bp
from .routes import routes_bp

def create_app():
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Validate configuration (skip if in testing mode)
    if not app.config.get('TESTING'):
        Config.validate_config()
    
    # Ensure JWT secret key is set (for testing)
    if not app.config.get('JWT_SECRET_KEY'):
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    return app
