import pytest
from .__init__ import create_test_app, db
from app.models import User, Equipment, Borrow
from werkzeug.security import generate_password_hash


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
    test_item = Equipment(Type="Apple", model="iPad Pro", serial_number="1234567", status='available', max_time=5)
    db.session.add(man)
    db.session.add(stud)
    db.session.add(test_item)
    db.session.commit()
    yield  # this is where the testing happens!
    db.session.query(User).delete()
    db.session.query(Equipment).delete()
    db.session.query(Borrow).delete()
    db.session.commit()
