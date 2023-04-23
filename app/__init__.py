from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
App_DataBase = "database.db"
#-----
#login_manager = LoginManager()


def create_app():
    app = Flask(_name_)
    app.config['SECRET_KEY'] = 'some key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{App_DataBase}'
    db.init_app(app)
    #-----
    #login_manager.init_app(app)

    # Specify the login page for unauthorized users
    #login_manager.login_view = 'auth.login'
    #-----

    from .auth import auth
    from .views import views
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    return app

def create_database(app):
    with app.app_context():
        if not path.exists(App_DataBase):
            db.create_all()
            print('Created Database!')

app = create_app()
create_database(app)
