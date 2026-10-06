"""
Authentication routes and logic.
"""

from flask import Blueprint, request, jsonify, redirect, url_for, make_response
from markupsafe import escape
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
    set_access_cookies,
)
from .models import db, User
from .config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    GET: Returns HTML form for registration
    POST: Expects JSON: {username, email, password}
    """
    if request.method == "GET":
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Register</title></head>
        <body>
            <h1>Register</h1>
            <form method="POST" action="/auth/register">
                <label for="username">Username:</label><br>
                <input type="text" id="username" name="username"><br>
                <label for="email">Email:</label><br>
                <input type="email" id="email" name="email"><br>
                <label for="password">Password:</label><br>
                <input type="password" id="password" name="password"><br><br>
                <input type="submit" value="Register">
            </form>
            <p>Already have an account? <a href="/auth/login">Login here</a></p>
        </body>
        </html>
        """
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Validate input
        if not data or not all(k in data for k in ("username", "email", "password")):
            return jsonify({"error": "Missing required fields"}), 400

        username = data["username"].strip()
        email = data["email"].strip()
        password = data["password"]

        # Basic validation
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        if "@" not in email:
            return jsonify({"error": "Invalid email format"}), 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 409

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Return JSON for API calls, redirect for form submissions
        if request.is_json:
            return (
                jsonify(
                    {"message": "User registered successfully", "user": user.to_dict()}
                ),
                201,
            )
        else:
            # Create token and set in cookie for form submissions
            access_token = create_access_token(identity=str(user.id))
            response = make_response(
                redirect(url_for("auth.welcome", username=username))
            )
            set_access_cookies(response, access_token)
            return response

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login user and return JWT access token.
    GET: Returns HTML form for login
    POST: Expects JSON: {username, password}
    """
    if request.method == "GET":
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Login</title></head>
        <body>
            <h1>Login</h1>
            <form method="POST" action="/auth/login">
                <label for="username">Username:</label><br>
                <input type="text" id="username" name="username"><br>
                <label for="password">Password:</label><br>
                <input type="password" id="password" name="password"><br><br>
                <input type="submit" value="Login">
            </form>
            <p>Don't have an account? <a href="/auth/register">Register here</a></p>
        </body>
        </html>
        """
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Validate input
        if not data or not all(k in data for k in ("username", "password")):
            return jsonify({"error": "Missing required fields"}), 400

        username = data["username"].strip()
        password = data["password"]

        # Find user
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create access token (identity must be a string)
        access_token = create_access_token(identity=str(user.id))

        # Return JSON for API calls, redirect for form submissions
        if request.is_json:
            return jsonify({"access_token": access_token, "user": user.to_dict()}), 200
        else:
            # Set token in cookie for form submissions
            response = make_response(
                redirect(url_for("auth.welcome", username=username))
            )
            set_access_cookies(response, access_token)
            return response

    except Exception as e:
        return jsonify({"error": "Login failed"}), 500


@auth_bp.route("/welcome/<username>")
def welcome(username):
    """
    Welcome page after successful login/registration.
    """
    safe_username = escape(username)
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Welcome</title></head>
    <body>
        <h1>Hello, {safe_username}!</h1>
        <p>You have successfully logged in.</p>
        <a href="/auth/logout">Logout</a>
    </body>
    </html>
    """


@auth_bp.route("/logout")
def logout():
    """
    Logout user and redirect to login page.
    """
    response = make_response(redirect(url_for("auth.login")))
    unset_jwt_cookies(response)
    return response


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get current user information.
    Requires valid JWT token.
    """
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id)) if current_user_id else None

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve user"}), 500
