from flask import Blueprint, render_template

auth = Blueprint("auth", __name__)


@auth.route('/login')
def login():
    return "<p>Login</p>"


@auth.route("/")
def home():
    return render_template("base.html")
