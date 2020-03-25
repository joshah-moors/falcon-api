# /bin/usr/env python3
'''
Integration test script for falcon-jwt-api

With the api running in the test environment, this script performs the following validations:
    • Fetch the public data
    • Create a new user on the user-mgmt endpoint
    • Fetch the public data as new user

'''

import json
import sys
import time
import traceback

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

# test session store for holding state between tests
tss = {}

test_collection = (
                    'test_fetch_public',
                    'test_fetch_private_fail',
                    'test_create_user',
                    'test_login',
                    'test_fetch_private_success',
                    'teardown',
                   )


def run_tests():
    try:
        for test in test_collection:
            exec(f'print("Running: {test}"); {test}(tss)')
        print('\n\t - ALL TESTS SUCCEEDED - \n')
    except Exception as e:
        print(f'\nFAILURE while running tests: {e}')
        traceback.print_exc()
        try:
            teardown(tss)
        except:
            print('Error removing test user from db')
        sys.exit(1)


def test_fetch_public(tss):
    r = requests.get(f'{BASE_URL}/media/api/v1/public')
    assert r.status_code == 200
    assert r.json()['data'] == 'it\'s all good'


def test_fetch_private_fail(tss):
    r = requests.get(f'{BASE_URL}/media/api/v1/private')
    assert r.status_code == 401
    assert r.json()['title'] == '401 Unauthorized'


def test_create_user(tss):
    r = requests.post(f'{BASE_URL}/auth/api/v1/user-mgmt',
                       data=json.dumps(test_user),
                       headers={'content-type': 'application/json'})
    assert r.status_code == 200
    assert r.json()['status'] == 'success'


def test_login(tss):
    r = requests.post(f'{BASE_URL}/auth/api/v1/login',
                       data=json.dumps(test_user),
                       headers={'content-type': 'application/json'})
    assert r.status_code == 200
    for key in ('accessToken', 'refreshToken', 'refreshAge'):
        assert key in r.json().keys()

    # Hold tokens for later test use
    for key, value in r.json().items():
        tss[key] = value


def test_fetch_private_success(tss):
    r = requests.get(f'{BASE_URL}/media/api/v1/private',
                       headers={'Authorization': f'JWT {tss["accessToken"]}'})
    assert r.status_code == 200
    assert r.json()['status'] == 'success'
    assert r.json()['data'] == 'joshah is cool (don\'t tell anyone)'


def teardown(tss):
    ''' clean-up test user made in db '''
    engine = create_engine('sqlite:///../jwtapi/db/backend.db')
    session = sessionmaker(bind=engine)()

    session.query(app_db.User)                                    \
           .filter(app_db.User.username == test_user['username']) \
           .delete()

    session.commit()
    session.close()
    

#def test_posted_image_gets_saved():
#    file_save_prefix = '/tmp/'
#    location_prefix = '/images/'
#    fake_image_bytes = b'fake-image-bytes'
#
#    response = requests.post(
#        'http://localhost:8000/images',
#        data=fake_image_bytes,
#        headers={'content-type': 'image/png'}
#    )
#
#    assert response.status_code == 201
#    location = response.headers['location']
#    assert location.startswith(location_prefix)
#    image_name = location.replace(location_prefix, '')
#
#    file_path = file_save_prefix + image_name
#    with open(file_path, 'rb') as image_file:
#        assert image_file.read() == fake_image_bytes
#
#    os.remove(file_path)

if __name__ == '__main__':
    run_tests()
