#! /usr/bin/env python3

import os

import falcon

from .images import Collection, Item, ImageStore

#api = application = falcon.API()

#image_store = ImageStore('.')
#images = Resource(image_store)
#api.add_route('/images', images)

# Refactor the above to dependency injection

#Command to start server
#    waitress-serve --port=8000 --call 'falconapi.app:get_app'

def create_app(image_store):
    api = falcon.API()
    api.add_route('/images', Collection(image_store))
    api.add_route('/images/{name}', Item(image_store))
    return api

def get_app():
    storage_path = os.environ.get('LOOK_STORAGE_PATH', '.')
    image_store = ImageStore(storage_path)
    return create_app(image_store)
