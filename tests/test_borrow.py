from flask import url_for, request
import pytest


def test_borrow(client, init_database):
    response = client.post('/login',
                           data=dict(email='stud@ac.sce.ac.il',
                                     password="Ab123456"),
                           follow_redirects=True)
    
    response = client.post('/borrow', follow_redirects=True)
    expected_url = url_for('views.borrow')
    assert response.request.path == expected_url
    

