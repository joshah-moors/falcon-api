#! /usr/bin/env python3

import json

import falcon
import pytest
from falcon import testing
from unittest import mock

import jwtapi.app
import jwtapi.app_db

test_user_dict = {
    'email': 'mr.fake@gmail.com',
    'username': 'fakeuser2020',
    'password': 'F@ke!s0NtheRI$e'
}

@pytest.fixture
def client():
    api = jwtapi.app.create_app()
    return testing.TestClient(api)


def test_public_route(client):
    ''' Test the open route '''
    response = client.simulate_get('/media/api/v1/public')
    assert response.status == falcon.HTTP_OK
    assert response.json['status'] == 'success'
    assert response.json['data'] == 'it\'s all good'

def test_private_route_no_auth(client):
    ''' Test the protected route '''
    response = client.simulate_get('/media/api/v1/private')
    assert response.status == falcon.HTTP_401
    assert response.json['title']  == '401 Unauthorized'
    assert response.json['description'] == 'Missing Authorization Header'

def test_invalidate_route_no_auth(client):
    ''' Test invalidate route - fail condition '''
    response = client.simulate_post('/auth/api/v1/invalidate')
    assert response.status == falcon.HTTP_401
    assert response.json['title']  == '401 Unauthorized'
    assert response.json['description'] == 'Missing Authorization Header'

def test_new_user_success(client, monkeypatch):
    ''' Test creating a new user - pass condition '''

    # monkeypatch the create user method
    monkeypatch.setattr('jwtapi.app_db.User.create', lambda self: (True, ''))

    body = json.dumps(test_user_dict)
    response = client.simulate_post('/auth/api/v1/user-mgmt', body=body)
    assert response.status == falcon.HTTP_OK
    assert response.json['status']  == 'success'

def test_new_user_fail(client, monkeypatch):
    ''' Test creating a new user - fail condition '''

    # monkeypatch the create user method
    fail_status = 'username taken'
    monkeypatch.setattr('jwtapi.app_db.User.create', lambda self: (False, fail_status))

    body = json.dumps(test_user_dict)
    response = client.simulate_post('/auth/api/v1/user-mgmt', body=body)
    assert response.status == falcon.HTTP_409
    assert response.json['status'] == fail_status

#def test_login(client, monkeypatch):
#    ''' Test the login endpoint - pass condition '''
#    #monkeypatch.setattr('req.context["db_session"].query', lambda obj: ['test'])
#    req = mock.Mock()
#    req.context['db_session'].query.return_value = ['test']
#
#    body = json.dumps(test_user_dict)
#    response = client.simulate_post('/auth/api/v1/login', body=body)
#    assert response.status == falcon.HTTP_OKs
    
