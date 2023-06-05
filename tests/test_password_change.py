from flask import url_for, request
import pytest
from app.models import User
from werkzeug.security import check_password_hash


def test_profile_pass_change(client, init_database):
    # login to student
    response = client.post('/login', data=dict(email='stud@ac.sce.ac.il',
                                               password="Ab123456"),
                            follow_redirects=True)
    
    # bad old password
    response = client.post('/profile', data=dict(old_pass="123134",
                                                 pass1="Ab654321",
                                                 pass2="Ab654321"),
                                        follow_redirects=True)
    # check that didnt changed
    user = User.query.filter_by(email='stud@ac.sce.ac.il').first()
    assert not check_password_hash(user.password, "123134")


    # bad new password
    response = client.post('/profile', data=dict(old_pass="Ab123456",
                                                 pass1="A123456",
                                                 pass2="A123456"),
                                        follow_redirects=True)
    # check that didnt changed
    user = User.query.filter_by(email='stud@ac.sce.ac.il').first()
    assert not check_password_hash(user.password, "A123456")


    # bad 2nd password
    response = client.post('/profile', data=dict(old_pass="Ab123456",
                                                 pass1="Ab654321",
                                                 pass2="Ab222222"),
                                        follow_redirects=True)
    # check that didnt changed
    user = User.query.filter_by(email='stud@ac.sce.ac.il').first()
    assert not check_password_hash(user.password, "Ab654321")

    # good input
    response = client.post('/profile', data=dict(old_pass="Ab123456",
                                                 pass1="Ab654321",
                                                 pass2="Ab654321"),
                                        follow_redirects=True)
    # check that changed
    user = User.query.filter_by(email='stud@ac.sce.ac.il').first()
    assert check_password_hash(user.password, "Ab654321")

    # logout
    response = client.post('/logout', follow_redirects=True)
    expected_url = url_for('auth.login')
    assert response.request.path == expected_url