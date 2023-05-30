import pytest
from .__init__ import create_test_app, db
from app.models import *
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


@pytest.fixture(scope='module')
def client():
    app = create_test_app()
    with app.test_client() as test_client: 
       with app.app_context(): 
        yield test_client


@pytest.fixture(scope='module')
def init_database(client):
    # Create the database and the database table
    db.create_all()
    man = User(userType="Manager", email="man@ac.sce.ac.il", name="jon doe", password=generate_password_hash("Ab123456", method='sha256'),phone="0525555555")
    stud = User(userType="Student", email="stud@ac.sce.ac.il", name="jane doe", password=generate_password_hash("Ab123456", method='sha256'),phone="0520000000")
    test_avai_item = Equipment(Type="Apple", model="iPad Pro", serial_number="1234567", status='available', max_time=5)
    test_bor_item = Equipment(Type="Rec", model="Rode micro mic", serial_number="111111", status='borrowed', max_time=3)
    db.session.add(man)
    db.session.add(stud)
    db.session.add(test_avai_item)
    db.session.add(test_bor_item)
    db.session.commit()

    user = User.query.filter_by(userType="Student").first()
    item = Equipment.query.filter_by(Type="Rec").first()
    todays_date = datetime.now().date()
    two_days_later = todays_date + timedelta(days=2)
    test_borrow = Borrow(borrower=user.id, aq_serial=item.serial_number, borrow_date=todays_date.strftime('%d/%m/%Y'), return_date=two_days_later.strftime('%d/%m/%Y'), return_status="no")
    db.session.add(test_borrow)
    db.session.commit()
    yield  # this is where the testing happens!
    db.session.query(Borrow).delete()
    db.session.query(Notification).delete()
    db.session.query(Room_Book).delete()    
    db.session.query(User).delete()
    db.session.query(Equipment).delete()   
    db.session.commit()
