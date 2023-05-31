from flask import url_for, request
from datetime import datetime, timedelta
import pytest
from app.models import User, Borrow


def test_transfer_borrow(client, init_database):
    # login to student
    response = client.post('/register', data=dict(name='פלוני אלמוני',
                                                  userType="Student",
                                                  phone="0521111111",
                                                  email="ploni@ac.sce.ac.il",
                                                  password1="Aa123456", 
                                                  password2="Aa123456"), 
                                        follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url

    # logout
    response = client.post('/logout', follow_redirects=True)
    expected_url = url_for('auth.login')
    assert response.request.path == expected_url

    #login to owner of borrow user
    response = client.post('/login', data=dict(email='stud@ac.sce.ac.il',
                                               password="Ab123456"),
                           follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url

    # try to transfer to manager (shouldn't transfer)
    to_man = User.query.filter_by(email="man@ac.sce.ac.il").first()
    borrow = Borrow.query.first()
    response = client.post('/check_trans', data=dict(aq_serial=borrow.aq_serial,
                                                     email=to_man.email),
                                           follow_redirects=True)
    expected_url = url_for('views.transfer_form')
    assert response.request.path == expected_url

    # transfer to the created user
    to_stud = User.query.filter_by(email="ploni@ac.sce.ac.il").first()   
    response = client.post('/check_trans', data=dict(aq_serial=borrow.aq_serial,
                                                     email=to_stud.email),
                                           follow_redirects=True)
    expected_url = url_for('views.user_borrowing')
    assert response.request.path == expected_url

    # check if the user updated
    assert borrow.return_status == "yes"
    borrow = Borrow.query.filter_by(borrower=to_stud.id)
    assert borrow is not None
