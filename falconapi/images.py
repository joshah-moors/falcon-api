#! /usr/bin/env python3

import io
import json
import os
import uuid
import mimetypes

import falcon
import msgpack

class Resource:

    # Initialize resource with path used during POST
    def __init__(self, image_store):
        self._image_store = image_store

    def on_get(self, req, resp):
        doc = {
            'images': [
                {
                    'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
                }

            ]
        }

        # Create a JSON representation of the resource
        #resp.body = json.dumps(doc, ensure_ascii=False)
        #
        # Give Message Pack a shot
        resp.data = msgpack.packb(doc, use_bin_type=True)
        resp.content_type = falcon.MEDIA_MSGPACK
        #
        # 200 is default
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        name = self._image_store.save(req.stream, req.content_type)
        #
        resp.status = falcon.HTTP_201
        resp.location = '/images/' + name


class ImageStore:

    _CHUNK_SIZE_BYTES = 4096

    # Note dependency injection for std library methods
    # This will avoid monkey-patching later
    def __init__(self, storage_path, uuidgen=uuid.uuid4, fopen=io.open):
        self._storage_path = storage_path
        self._uuid_gen = uuidgen
        self._fopen = fopen

    def save(self, image_stream, image_content_type):
        ext = mimetypes.guess_extension(image_content_type)
        name = f'{self._uuid_gen()}{ext}'
        image_path = os.path.join(self._storage_path, name)

        with self._fopen(image_path, 'wb') as image_file:
            while True:
                chunk = image_stream.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                image_file.write(chunk)

        return name
