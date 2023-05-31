from flask import url_for, request
from datetime import datetime, timedelta
import pytest
from app.models import Notification


def test_borrow_noti(client, init_database):
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

    # check the notification count
    response = client.get('/notifications/count')
    data = response.json
    assert 'count' in data
    count = data['count']
    assert count == 1


def test_seen_borrow_noti(client):
    noti = Notification.query.first()
    assert noti is not None


    # mark the notification as read
    response = client.post('/seen_notification?notif_id='+str(noti.id),
                           follow_redirects=True)
    expected_url = url_for('views.notifications')
    assert response.request.path == expected_url

    # check if count is reduced
    response = client.get('/notifications/count')
    data = response.json
    assert 'count' in data
    count = data['count']
    assert count == 0