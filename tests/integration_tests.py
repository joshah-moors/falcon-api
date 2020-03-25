#! /bin/usr/env python3
'''
Integration test script for falcon-jwt-api

With the api running in the test environment, this script performs the following validations:
    • Fetch the public data
    • Create a new user on the user-mgmt endpoint
    • Fetch the public data as new user

'''

import requests

def run_test():
    try:
        test_collection = ('fetch_public',)
        for test in test_collection:
            exec(f'print("  Running: {test}"); {test}()')
        print('\nAll tests SUCCEEDED')
    except Exception as e:
        print(f'FAILURE while running tests: {e}')

def fetch_public():
    r = requests.get('http://localhost:8000/media/api/v1/public')
    response_json = r.json()
    assert response_json['data'] == 'it\'s all good'

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
    run_test()