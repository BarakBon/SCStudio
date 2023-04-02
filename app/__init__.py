from flask import Flask
from os import path
from flask_login import LoginManager


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'some key'

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

    return app
