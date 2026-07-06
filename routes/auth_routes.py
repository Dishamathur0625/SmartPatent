from flask import Blueprint, render_template, request, redirect, session
from models.user_model import UserModel
from werkzeug.security import generate_password_hash, check_password_hash
import re
import secrets
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)
user_model = UserModel()

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Backend Input Validation
        if not name or not email or not password:
            return render_template("signup.html", error="All fields are required.")
        
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            return render_template("signup.html", error="Please enter a valid email address.")
            
        if len(password) < 8:
            return render_template("signup.html", error="Password must be at least 8 characters long.")

        try:
            # Check for duplicate registration to prevent database crash
            existing_user = user_model.get_user_by_email(email)
            if existing_user:
                return render_template("signup.html", error="Email is already registered.")

            hashed_password = generate_password_hash(password)
            user_model.create_user(name, email, hashed_password)
            return redirect("/login")
        except Exception as e:
            return render_template("signup.html", error="An error occurred during registration. Please try again.")

    return render_template("signup.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="Please provide both email and password.")

        user = user_model.get_user_by_email(email)

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            return render_template("forgot_password.html", error="Email address is required.")

        user = user_model.get_user_by_email(email)
        if not user:
            # Prevent user enumeration security scan alerts by returning a generic soft success statement
            return render_template("forgot_password.html", success="If your email is registered in our database, a password reset link has been logged to the server stdout/console.")

        # Create 1-hour active reset token
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=1)
        user_model.set_password_reset_token(email, token, expiry)

        # Log reset url locally (since SMTP server is not set up on local systems)
        reset_link = f"http://127.0.0.1:5000/reset_password/{token}"
        print(f"\n[SECURITY AUDIT LOG] PASSWORD RESET LINK FOR {email}: {reset_link}\n", flush=True)

        return render_template("forgot_password.html", success="A password reset link has been generated and logged to the server console. Please check the terminal logs.")

    return render_template("forgot_password.html")

@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = user_model.get_user_by_reset_token(token)
    if not user:
        return render_template("reset_password.html", error="Invalid or expired password reset token.")

    if request.method == "POST":
        password = request.form.get("password", "")
        if not password or len(password) < 8:
            return render_template("reset_password.html", error="Password must be at least 8 characters long.")

        hashed_password = generate_password_hash(password)
        user_model.update_password(user["user_id"], hashed_password)
        user_model.clear_password_reset_token(user["user_id"])

        return render_template("login.html", success="Password reset successful! You can now log in.")

    return render_template("reset_password.html", token=token)