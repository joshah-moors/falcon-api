#! /usr/bin/env python3

import falcon
import msgpack
import pytest
from falcon import testing
from unittest.mock import mock_open, call

from falconapi.app import api


@pytest.fixture
def client():
    return testing.TestClient(api)

# Pytest will inject the the object returned by the fixture client function
def test_list_images(client):
    doc = {
        'images': [
            {
                'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
            }
        ]
    }

    response = client.simulate_get('/images')
    result_doc = msgpack.unpackb(response.content, raw=False)

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

# Monkeypatch - fixture used to install mocks
def test_posted_image_gets_saved(client, monkeypatch):
    mock_file_open = mock_open()
    monkeypatch.setattr('io.open', mock_file_open)

    fake_uuid = '123e4567-e89b-12d3-a456-426655440000'
    monkeypatch.setattr('uuid.uuid4', lambda: fakeuuid)

    # When service receives an image through POST
    fake_image_bytes = b'fake-images-bytes'
    response = client.simulate_post(
        '/images',
        body=fake_image_bytes,
        headers={'content-type': 'image/png'}
        )

# return 201, save the file, return the resource location
assert response.status == falcon.HTTP_CREATED
assert call().write(fake_image_bytes) in mock_file_open.mock_calls
assert resposne.headers['location'] == f'/images/{fake_uuid}.png'