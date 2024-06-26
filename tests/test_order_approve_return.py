from flask import url_for, request
from datetime import datetime, timedelta
import pytest
from app.models import Borrow, Room_Book


def test_borrow_approve_and_return(client, init_database):
    # login to student
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

    # login to manager
    response = client.post('/login', data=dict(email='man@ac.sce.ac.il',
                                               password="Ab123456"),
                           follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url

    # make new borrow
    borrow = Borrow.query.filter_by(aq_serial="1234567").first()
    response = client.post('/eq_transfer', data=dict(borrow_id=borrow.id),
                           follow_redirects=True)
    expected_url = url_for('views.eq_transfer')
    assert response.request.path == expected_url

    #check the item changed to borrowed
    assert borrow.item.status == "borrowed"

    # return the borrow
    response = client.post('/report_return', data=dict(borrow_id=borrow.id),
                           follow_redirects=True)
    expected_url = url_for('views.borrowed_equipment')
    assert response.request.path == expected_url

    # check for statuses
    assert borrow.item.status == "available"
    assert borrow.return_status == "yes"




def test_room_book(client):
    todays_date = datetime.now().date()

    # make room order
    response = client.post('/rooms', data=dict(type="studio",
                                               date=str(todays_date),
                                               time="12:00"),
                           follow_redirects=True)
    expected_url = url_for('views.user_borrowing')
    assert response.request.path == expected_url

    # check if the book added
    book = Room_Book.query.first()
    assert book is not None
    
    # logout
    response = client.post('/logout', follow_redirects=True)
    expected_url = url_for('auth.login')
    assert response.request.path == expected_url