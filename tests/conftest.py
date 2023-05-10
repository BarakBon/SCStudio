import pytest
from .__init__ import create_test_app, db


@pytest.fixture(scope='module')
def client():
    app = create_test_app()
    with app.test_client() as test_client:
        #with client.app_context():
        #    db.create_all()
        yield test_client


@pytest.fixture(scope='module')
def init_database(client):
    # Create the database and the database table
    db.create_all()
    db.session.commit()
    yield  # this is where the testing happens!
