from flask import url_for, request
from datetime import datetime, timedelta
import pytest
from app.models import Borrow, Room_Book


def test_faulty_item(client, init_database):
    # login to manager
    response = client.post('/login', data=dict(email='man@ac.sce.ac.il',
                                               password="Ab123456"),
                           follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url

    #report the borrowed item as faulty
    borrow = Borrow.query.first()
    response = client.post('/report_fault', data=dict(borrow_id=borrow.id),
                           follow_redirects=True)
    expected_url = url_for('views.borrowed_equipment')
    assert response.request.path == expected_url

    #check if the statuses changed
    borrow = Borrow.query.first()
    assert borrow.return_status == "yes"
    assert borrow.item.status == "faulty"

