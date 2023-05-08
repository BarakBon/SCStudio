from . import db
from flask_login import UserMixin


class Equipment(db.Model, UserMixin):
    Type= db.Column(db.String(10))
    model=db.Column(db.String(50))
    serial_number= db.Column(db.String(50), primary_key=True)
    status = db.Column(db.String(15))
    max_time = db.Column(db.Integer) # in days
    
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userType = db.Column(db.String(8))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    name = db.Column(db.String(50))


class Borrow(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    borrower = db.Column(db.Integer, db.ForeignKey('user.id'))
    aq_serial = db.Column(db.String(50), db.ForeignKey('equipment.serial_number'))
    borrow_date = db.Column(db.String(10)) # for now dd/mm/yyyy may be changed later
    return_date = db.Column(db.String(10)) # ^


class Room_Book(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(8)) # podcast / studio
    inviter = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(10)) # for now dd/mm/yyyy may be changed later
    start_hour = db.Column(db.Integer) # will be in 'hh' (hour) format 
    end_hour = db.Column(db.Integer) # ^

'''from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))'''

    