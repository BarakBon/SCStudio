from flask import Flask
from os import path
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
User_Det = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'some key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{User_Det}'
    db.init_app(app)

    from .auth import auth
    from .views import views
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    from app.models.user import User
    create_database(app)

    return app

def create_database(app):
    if not path.exists('app/' + User_Det):
        db.create_all(app=app)
        print('Created Database!')