from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pytest

db = SQLAlchemy()

def create_test_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'some key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:scstudio@main-database.ce63v0984odx.eu-central-1.rds.amazonaws.com:3306/test_scstudio'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)

    
    from app.auth import auth
    app.register_blueprint(auth)
    from app.views import views
    app.register_blueprint(views)

    
    from app.models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    
    #with app.test_client() as client:
    with app.app_context():
        db.create_all()
        '''
        yield client
        with app.app_context():
            db.drop_all()
        '''
    return app

