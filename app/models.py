from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    #__tablename__ = 'users'
    email = db.Column(db.String(150), unique=True, primary_key=True)
    password = db.Column(db.String(150))
    phone = db.Column(db.String(10))
    name = db.Column(db.String(150))
    phone = db.Column(db.Integer)
    
