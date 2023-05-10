import pytest
from .__init__ import create_test_app, db
from app.models import User
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
    test_user = User(userType="Student", email="test@ac.sce.ac.il", name="jon doe", password=generate_password_hash("Ab123456", method='sha256'),phone="0525555555")
    db.session.add(test_user)
    db.session.commit()
    yield  # this is where the testing happens!
    User.query.filter_by(id=test_user.id).delete()
    db.session.commit()
