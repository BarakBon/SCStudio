from flask import url_for
import pytest


def test_index_page(client):
    response = client.get('/login')
    assert response.status_code == 200


