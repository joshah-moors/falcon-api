#! /usr/bin/env python3

import falcon
import msgpack
import pytest
from falcon import testing

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
