from flask import url_for, request
from datetime import datetime, timedelta
import pytest
from app.models import Equipment


def test_adding_item(client, init_database):
    # login to manager
    response = client.post('/login', data=dict(email='man@ac.sce.ac.il',
                                               password="Ab123456"),
                           follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url

    # adding new item
    response = client.post('/adding_equipment', data=dict(type='Camera',
                                                model="Sony A7III",
                                                serialNumber="7894565",
                                                maxTime="3"),
                           follow_redirects=True)
    expected_url = url_for('views.equipment')
    assert response.request.path == expected_url

    # checking if added
    item = Equipment.query.filter_by(Type="Camera").first()
    assert item is not None
