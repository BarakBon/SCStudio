from . import db
from flask_login import UserMixin

class Borrowed_Equipment(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Type= db.Column(db.String(10))
    model=db.Column(db.String(150))
    pickup_date = db.Column(db.DATE )
    return_date = db.Column(db.DATE )
    
class Equipment(db.Model, UserMixin):
    Type= db.Column(db.String(10))
    model=db.Column(db.String(150))
    Serial_Number= db.Column(db.String(150), primary_key=True)
    Available = db.Column(db.String(150))
    Time = db.Column(db.String(150))
    
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userType = db.Column(db.String(8))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    phone = db.Column(db.String(10))
    name = db.Column(db.String(150))

