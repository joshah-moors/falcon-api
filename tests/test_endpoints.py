#! /usr/bin/env python3

import json

import falcon
import pytest
from falcon import testing

import jwtapi.app
import jwtapi.app_db

mock_user_dict = {
    'email': 'mr.fake@gmail.com',
    'username': 'fakeuser2020',
    'password': 'F@ke!s0NtheRI$e'
}


@pytest.fixture
def client():
    api = jwtapi.app.create_app()
    return testing.TestClient(api)


class DBSessionPath:
    def __init__(self, records):
        self.records = records

    def all(self):
        return self.records

    def delete(self, **kwargs):
        return self

    def filter(self, x):
        return self

    def join(self, x):
        return self


# Route: /auth/api/v1/login


def test_login_no_params(client):
    ''' Test login route, no params - fail condition '''
    response = client.simulate_post('/auth/api/v1/login')
    assert response.status == falcon.HTTP_409
    assert response.json['status'] == 'missing username/password'


def test_login_missing_params(client, monkeypatch):
    ''' Test login route, missing params - fail condition '''

    # patch request input
    monkeypatch.setattr('falcon.request.Request.media', {'username': 'fakeuser2020'})

    response = client.simulate_post('/auth/api/v1/login')
    assert response.status == falcon.HTTP_409
    assert response.json['status'] == 'missing username/password'


def test_login_no_user_found(client, monkeypatch):
    ''' Test login route - fail condition '''

    # patch request input & bypass auth
    media_dict = {k:v for k, v in mock_user_dict.items() if k != 'email'}
    monkeypatch.setattr('falcon.request.Request.media', media_dict)
    monkeypatch.setattr('sqlalchemy.orm.session.Session.query', lambda x, y: DBSessionPath([]))

    response = client.simulate_post('/auth/api/v1/login')
    assert response.status == falcon.HTTP_409
    assert response.json['status'] == 'user not found'


def test_login_no_pw_match(client, monkeypatch):
    ''' Test login route, no password match - fail condition '''

    # patch request input & bypass auth
    media_dict = {k: v for k, v in mock_user_dict.items() if k != 'email'}
    mock_user = jwtapi.app_db.User(
        mock_user_dict['username'],
        'some_pw_hash',
        mock_user_dict['email'])
    monkeypatch.setattr('falcon.request.Request.media', media_dict)
    monkeypatch.setattr('sqlalchemy.orm.session.Session.query', lambda x, y: DBSessionPath([mock_user]))

    response = client.simulate_post('/auth/api/v1/login')
    assert response.status == falcon.HTTP_401


def test_login_success(client, monkeypatch):
    ''' Test login route, hash match - success condition '''

    # patch request input & db functions
    media_dict = {k: v for k, v in mock_user_dict.items() if k != 'email'}
    mock_user = jwtapi.app_db.User(
        mock_user_dict['username'],
        jwtapi.app_db.hash_this(mock_user_dict['password'], jwtapi.app_db.SALT),
        mock_user_dict['email'])
    monkeypatch.setattr('falcon.request.Request.media', media_dict)
    monkeypatch.setattr('sqlalchemy.orm.session.Session.query', lambda x, y: DBSessionPath([mock_user]))
    monkeypatch.setattr('sqlalchemy.orm.session.Session.add', lambda x, y: True)
    monkeypatch.setattr('sqlalchemy.orm.session.Session.commit', lambda x: True)

    response = client.simulate_post('/auth/api/v1/login')
    assert response.status == falcon.HTTP_OK


# Route: /auth/api/v1/refresh


def test_refresh_route_no_auth(client):
    ''' Test refresh route - fail condition '''
    response = client.simulate_post('/auth/api/v1/refresh')
    assert response.status == falcon.HTTP_401


def test_refresh_no_token(client, monkeypatch):
    ''' Test refresh route, no token in body - fail condition'''
    monkeypatch.setattr('falcon.request.Request.media', {'user': 'fake'})

    response = client.simulate_post('/auth/api/v1/refresh')
    assert response.status == falcon.HTTP_401


def test_refresh_invalid_token(client, monkeypatch):
    ''' Test refresh route, with invalid token in header'''
    monkeypatch.setattr('falcon.request.Request.media', {'refreshToken': 'fake'})

    response = client.simulate_post('/auth/api/v1/refresh')
    assert response.status == falcon.HTTP_401


def test_refresh_no_secret_in_db(client, monkeypatch):
    ''' Test refresh route, with invalid token in header'''
    mock_refresh_secret = 'abcd-1234-efgh'
    mock_payload = {'user': {
                        'username': mock_user_dict['username'],
                        'refresh': mock_refresh_secret
                    }}

    monkeypatch.setattr('falcon.request.Request.media', {'refreshToken': mock_refresh_secret})
    monkeypatch.setattr('jwt.decode', lambda **kwargs: mock_payload)
    monkeypatch.setattr('sqlalchemy.orm.session.Session.query', lambda x, y: DBSessionPath([]))

    response = client.simulate_post('/auth/api/v1/refresh')
    assert response.status == falcon.HTTP_409
    assert response.json['status'] == 'user/token not found'


def test_refresh_valid(client, monkeypatch):
    ''' Test refresh route - success case '''
    mock_refresh_secret = 'abcd-1234-efgh'
    mock_payload = {'user': {
                        'username': mock_user_dict['username'],
                        'refresh': mock_refresh_secret
                    }}
    mock_user = jwtapi.app_db.User(
        mock_user_dict['username'],
        jwtapi.app_db.hash_this(mock_user_dict['password'], jwtapi.app_db.SALT),
        mock_user_dict['email'])

    class MockToken:
        token_secret = mock_refresh_secret

    monkeypatch.setattr('falcon.request.Request.media', {'refreshToken': mock_refresh_secret})
    monkeypatch.setattr('jwt.decode', lambda **kwargs: mock_payload)
    monkeypatch.setattr('sqlalchemy.orm.session.Session.query', lambda x, y: DBSessionPath([mock_user]))
    monkeypatch.setattr('sqlalchemy.orm.session.Session.add', lambda x, y: True)
    monkeypatch.setattr('sqlalchemy.orm.session.Session.commit', lambda x: True)
    monkeypatch.setattr('jwtapi.app_db.User.refresh_token', MockToken())

    response = client.simulate_post('/auth/api/v1/refresh')
    assert response.status == falcon.HTTP_OK
    for attr in ('accessToken', 'refreshToken', 'refreshAge'):
        assert attr in response.json


# Route: /auth/api/v1/invalidate


def test_invalidate_route_no_auth(client):
    ''' Test invalidate route - fail condition '''
    response = client.simulate_post('/auth/api/v1/invalidate')
    assert response.status == falcon.HTTP_401
    assert response.json['title'] == '401 Unauthorized'
    assert response.json['description'] == 'Missing Authorization Header'


def test_invalidate(client, monkeypatch):
    ''' Test invalidate route - pass condition '''

    # path middleware to set context
    monkeypatch.setattr('falcon_auth.JWTAuthBackend.authenticate', lambda w, x, y, z: {'id': 1})

    response = client.simulate_post('/auth/api/v1/invalidate')
    assert response.status == falcon.HTTP_OK


# Route: /auth/api/v1/user-mgmt


def test_new_user_success(client, monkeypatch):
    ''' Test creating a new user - pass condition '''

    # monkeypatch the create user method
    monkeypatch.setattr('jwtapi.app_db.User.create', lambda self: (True, ''))

    body = json.dumps(mock_user_dict)
    response = client.simulate_post('/auth/api/v1/user-mgmt', body=body)
    assert response.status == falcon.HTTP_OK
    assert response.json['status'] == 'success'


def test_new_user_fail(client, monkeypatch):
    ''' Test creating a new user - fail condition '''

    # monkeypatch the create user method
    fail_status = 'username taken'
    monkeypatch.setattr('jwtapi.app_db.User.create', lambda self: (False, fail_status))

    body = json.dumps(mock_user_dict)
    response = client.simulate_post('/auth/api/v1/user-mgmt', body=body)
    assert response.status == falcon.HTTP_409
    assert response.json['status'] == fail_status


# Route: /media/api/v1/public


def test_public_route(client):
    ''' Test the open route '''
    response = client.simulate_get('/media/api/v1/public')
    assert response.status == falcon.HTTP_OK
    assert response.json['status'] == 'success'
    assert response.json['data'] == 'it\'s all good'


# Route: /media/api/v1/private


def test_private_route_no_auth(client):
    ''' Test the protected route - fail case '''
    response = client.simulate_get('/media/api/v1/private')
    assert response.status == falcon.HTTP_401
    assert response.json['title'] == '401 Unauthorized'
    assert response.json['description'] == 'Missing Authorization Header'


def test_private_route_mock_auth(client, monkeypatch):
    ''' Test the protected route - success case '''

    # path middleware to set context
    monkeypatch.setattr('falcon_auth.JWTAuthBackend.authenticate', lambda w, x, y, z: {'id': 1})

    response = client.simulate_get('/media/api/v1/private')
    assert response.status == falcon.HTTP_OK
    assert response.json['status'] == 'success'
    assert response.json['data'] == 'joshah is cool (don\'t tell anyone)'
