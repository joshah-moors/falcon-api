#! /usr/bin/env python3

import falcon
import pytest

import jwtapi.app


@pytest.fixture
def client():
    api = jwtapi.app.create_app()
    return falcon.testing.TestClient(api)


def test_the_testcase(client):
    ''' Test the open route '''
    response = client.simulate_get('/media/api/v1/public')
    assert response.status == falcon.HTTP_OK
    assert response.json['status'] == 'success'
    assert response.json['data'] == 'it\'s all good'
