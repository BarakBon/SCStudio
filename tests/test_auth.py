from flask import url_for, request
import pytest
from werkzeug.security import generate_password_hash


def test_login_page(client, init_database):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'email' in response.data
    assert b'password' in response.data
    #bad login
    response = client.post('/login',
                           data=dict(email='test@ac.sce.ac.il',
                                     password="Ab111111"),
                           follow_redirects=True)
    response.status_code == 200
    #good login
    response = client.post('/login',
                           data=dict(email='test@ac.sce.ac.il',
                                     password="Ab123456"),
                           follow_redirects=True)
    response.status_code == 302