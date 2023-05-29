from flask import url_for, request
from datetime import datetime, timedelta
import pytest
from app.models import Borrow


def test_borrow_and_approve(client, init_database):
    #login to student
    response = client.post('/login', data=dict(email='stud@ac.sce.ac.il',
                                               password="Ab123456"),
                                     follow_redirects=True)
    
    todays_date = datetime.now().date()
    two_days_later = todays_date + timedelta(days=2)
    # open borrow
    response = client.post('/borrow', data=dict(type='Apple',
                                                model="iPad Pro",
                                                pickup_date=str(todays_date),
                                                return_date=str(two_days_later)),
                                      follow_redirects=True)
    expected_url = url_for('views.user_borrowing')
    assert response.request.path == expected_url

    # logout
    response = client.post('/logout', follow_redirects=True)
    expected_url = url_for('auth.login')
    assert response.request.path == expected_url

    #login to manager
    response = client.post('/login', data=dict(email='man@ac.sce.ac.il',
                                               password="Ab123456"),
                                     follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url
    
    #make new borrow
    borrow = Borrow.query.first()
    response = client.post('/eq_transfer', data=dict(borrow_id=borrow.id),
                                     follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url
    
    assert borrow.item.status == "borrowed"

    # logout
    response = client.post('/logout', follow_redirects=True)
    expected_url = url_for('auth.login')
    assert response.request.path == expected_url

    