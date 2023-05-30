from flask import url_for, request
import pytest
from werkzeug.security import generate_password_hash


def test_register(client, init_database):
    # bad email
    response = client.post('/register', data=dict(name='פלוני אלמוני',
                                                  userType="Student",
                                                  phone="0521111111",
                                                  email="ploni@gmail.com",
                                                  password1="Aa123456", 
                                                  password2="Aa123456"), 
                                        follow_redirects=True)
    expected_url = url_for('auth.register')
    assert response.request.path == expected_url

    # bad phone
    response = client.post('/register', data=dict(name='פלוני אלמוני',
                                                  userType="Student",
                                                  phone="05211",
                                                  email="ploni@ac.sce.ac.il",
                                                  password1="Aa123456", 
                                                  password2="Aa123456"), 
                                        follow_redirects=True)
    assert response.request.path == expected_url

    # missmatch password
    response = client.post('/register', data=dict(name='פלוני אלמוני',
                                                  userType="Student",
                                                  phone="0521111111",
                                                  email="ploni@ac.sce.ac.il",
                                                  password1="Aa123456", 
                                                  password2="Aa123477"), 
                                        follow_redirects=True)
    assert response.request.path == expected_url

    # good register
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



def test_login_logout(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'email' in response.data
    assert b'password' in response.data

    # bad login
    response = client.post('/login',
                           data=dict(email='man@ac.sce.ac.il',
                                     password="Ab111111"),
                           follow_redirects=True)
    expected_url = url_for('auth.login')
    assert response.request.path == expected_url

    # good login
    response = client.post('/login',
                           data=dict(email='man@ac.sce.ac.il',
                                     password="Ab123456"),
                           follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url

    # logout
    response = client.post('/logout', follow_redirects=True)
    expected_url = url_for('auth.login')
    assert response.request.path == expected_url

    