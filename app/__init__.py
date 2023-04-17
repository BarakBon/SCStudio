from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
App_DataBase = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'some key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{App_DataBase}'
    db.init_app(app)

    from .auth import auth
    from .views import views
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    from .models import User

    return app

def create_database(app):
    with app.app_context():
        if not path.exists(App_DataBase):
            db.create_all()
            print('Created Database!')

app = create_app()
create_database(app)