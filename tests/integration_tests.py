#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Integration test script for falcon-jwt-api

With the api running in the test environment, this script performs the following validations:
    • Fetch the public data
    • Test private endpoint is locked down
    • Create a new user
    • Login/receive token as new user
    • Fetch the private data
    • Use refresh token to obtain new access token
    • Invalidate the refresh token
    • Try to use invalid refresh token to get new access token

Afer all runs, incliding fail condition,
teardown function clears test user from the db

'''

import json
import sys
import time
import traceback

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append('../jwtapi/')
import app_db

BASE_URL = 'http://localhost:8000'

test_user = {
    'username': f'test_{str(round(time.time()))}',
    'email': f'test_user_{str(round(time.time()))}@testmail.com',
    'password': 'this_test_P@$sW0%D'
}

# Class instantiated in the session fixture to hold test state
class State:
    data = {}


@pytest.fixture(scope='session')
def ts() -> State:
    test_state = State()
    return test_state


@pytest.fixture(scope="session", autouse=True)
def final_teardown(request):
    ''' clean-up test user made in db '''
    def db_cleanup():
        engine = create_engine('sqlite:///../jwtapi/db/backend.db')
        session = sessionmaker(bind=engine)()
        session.query(app_db.User)                                    \
               .filter(app_db.User.username == test_user['username']) \
               .delete()
        session.commit()
        session.close()
    request.addfinalizer(db_cleanup)


def test_fetch_public():
    r = requests.get(f'{BASE_URL}/api/v1/media/public')
    assert r.status_code == 200
    assert r.json()['data'] == 'it\'s all good'


def test_fetch_private_fail():
    r = requests.get(f'{BASE_URL}/api/v1/media/private')
    assert r.status_code == 401
    assert r.json()['title'] == '401 Unauthorized'


def test_create_user():
    r = requests.post(f'{BASE_URL}/api/v1/auth/user-mgmt',
                       data=json.dumps(test_user),
                       headers={'content-type': 'application/json'})
    assert r.status_code == 200
    assert r.json()['status'] == 'success'


def test_login(ts: State):
    r = requests.post(f'{BASE_URL}/api/v1/auth/login',
                       data=json.dumps(test_user),
                       headers={'content-type': 'application/json'})
    assert r.status_code == 200
    for key in ('accessToken', 'refreshToken', 'refreshAge'):
        assert key in r.json().keys()

    # Hold tokens for later test use
    for key, value in r.json().items():
        ts.data[key] = value


def test_fetch_private_success(ts: State):
    r = requests.get(f'{BASE_URL}/api/v1/media/private',
                       headers={'Authorization': f'JWT {ts.data["accessToken"]}'})
    assert r.status_code == 200
    assert r.json()['status'] == 'success'
    assert r.json()['data'] == 'joshah is cool (don\'t tell anyone)'


def test_refresh_token(ts: State):
    r = requests.post(f'{BASE_URL}/api/v1/auth/refresh',
                       data=json.dumps({'refreshToken': ts.data['refreshToken']}),
                       headers={'content-type': 'application/json'})
    assert r.status_code == 200
    for key in ('accessToken', 'refreshToken', 'refreshAge'):
        assert key in r.json().keys()

    # Update tokens in test store
    for key, value in r.json().items():
        ts.data[key] = value


def test_invalidate_token(ts: State):
    r = requests.post(f'{BASE_URL}/api/v1/auth/invalidate',
                        headers={'Authorization': f'JWT {ts.data["accessToken"]}'})
    assert r.status_code == 200


def test_refrest_with_invalid_token(ts: State):
    r = requests.post(f'{BASE_URL}/api/v1/auth/refresh',
                       data=json.dumps({'refreshToken': ts.data['refreshToken']}),
                       headers={'content-type': 'application/json'})

    assert r.status_code == 409
    assert r.json()['status'] == 'user/token not found'


if __name__ == '__main__':
    pytest.main([__file__])
