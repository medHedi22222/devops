"""
Main application routes.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    Returns simple status to verify the application is running.
    """
    return jsonify({'status': 'ok'}), 200

@routes_bp.route('/', methods=['GET'])
def index():
    """
    Root endpoint.
    Returns basic information about the API.
    """
    return jsonify({
        'message': 'DevSecOps Flask API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'register': '/auth/register',
            'login': '/auth/login',
            'me': '/auth/me',
            'protected': '/protected'
        }
    }), 200

@routes_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """
    Protected demo route.
    Requires valid JWT token to access.
    """
    return jsonify({'message': 'This is a protected route', 'status': 'success'}), 200
