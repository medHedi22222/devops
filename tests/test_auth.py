"""
Pytest tests for authentication functionality.
Tests cover register, login, and protected routes with JWT tokens.
"""

import os
import pytest
from app import create_app
from app.models import db, User

@pytest.fixture
def app():
    """Create and configure a test application instance."""
    # Set required environment variables for testing
    os.environ['SECRET_KEY'] = 'test-secret-key-for-testing'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-testing-must-be-32-bytes'
    os.environ['JWT_ACCESS_TOKEN_EXPIRES'] = '900'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # Ensure JWT config is properly set for testing
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-testing-must-be-32-bytes'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('TestPassword123')
        db.session.add(user)
        db.session.commit()
        return user

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}

def test_register_user_success(client):
    """Test successful user registration."""
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'SecurePassword123'
    })
    assert response.status_code == 201
    data = response.json
    assert data['message'] == 'User registered successfully'
    assert 'user' in data
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'newuser@example.com'
    assert 'password_hash' not in data['user']

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username."""
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'different@example.com',
        'password': 'SecurePassword123'
    })
    assert response.status_code == 409
    assert 'Username already exists' in response.json['error']

def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post('/auth/register', json={
        'username': 'different',
        'email': 'test@example.com',
        'password': 'SecurePassword123'
    })
    assert response.status_code == 409
    assert 'Email already exists' in response.json['error']

def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    response = client.post('/auth/register', json={
        'username': 'newuser'
    })
    assert response.status_code == 400
    assert 'Missing required fields' in response.json['error']

def test_register_short_password(client):
    """Test registration with password too short."""
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'short'
    })
    assert response.status_code == 400
    assert 'Password must be at least 8 characters' in response.json['error']

def test_register_short_username(client):
    """Test registration with username too short."""
    response = client.post('/auth/register', json={
        'username': 'ab',
        'email': 'newuser@example.com',
        'password': 'SecurePassword123'
    })
    assert response.status_code == 400
    assert 'Username must be at least 3 characters' in response.json['error']

def test_register_invalid_email(client):
    """Test registration with invalid email format."""
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'invalidemail',
        'password': 'SecurePassword123'
    })
    assert response.status_code == 400
    assert 'Invalid email format' in response.json['error']

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    assert response.status_code == 200
    data = response.json
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['username'] == 'testuser'

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'WrongPassword'
    })
    assert response.status_code == 401
    assert 'Invalid credentials' in response.json['error']

def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post('/auth/login', json={
        'username': 'nonexistent',
        'password': 'SomePassword'
    })
    assert response.status_code == 401
    assert 'Invalid credentials' in response.json['error']

def test_login_missing_fields(client):
    """Test login with missing required fields."""
    response = client.post('/auth/login', json={
        'username': 'testuser'
    })
    assert response.status_code == 400
    assert 'Missing required fields' in response.json['error']

def test_protected_route_with_token(client, test_user):
    """Test protected route with valid JWT token."""
    # First login to get token
    login_response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    token = login_response.json['access_token']
    
    # Access protected route with token
    response = client.get('/protected', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'This is a protected route'

def test_protected_route_without_token(client):
    """Test protected route without JWT token."""
    response = client.get('/protected')
    assert response.status_code == 401

def test_protected_route_with_invalid_token(client):
    """Test protected route with invalid JWT token."""
    response = client.get('/protected', headers={
        'Authorization': 'Bearer invalidtoken123'
    })
    assert response.status_code == 422

def test_get_current_user_with_token(client, test_user):
    """Test /auth/me endpoint with valid JWT token."""
    # First login to get token
    login_response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    token = login_response.json['access_token']
    
    # Access /auth/me with token
    response = client.get('/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    data = response.json
    assert 'user' in data
    assert data['user']['username'] == 'testuser'
    assert data['user']['email'] == 'test@example.com'

def test_get_current_user_without_token(client):
    """Test /auth/me endpoint without JWT token."""
    response = client.get('/auth/me')
    assert response.status_code == 401
