from flask import Blueprint, render_template, request, redirect, session
from models.user_model import UserModel
import hashlib

auth = Blueprint('auth', __name__)

user_model = UserModel()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@auth.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = hash_password(password)

        user_model.create_user(name, email, hashed_password)

        return redirect("/login")

    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        hashed_password = hash_password(password)

        user = user_model.get_user_by_email(email)

        if user and user["password"] == hashed_password:

            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]

            return redirect("/dashboard")

        else:
            return "Invalid email or password"

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()
    return redirect("/")