#! /usr/bin/env python3

import falcon

from .images import Resource

api = application = falcon.API()

api.add_route('/images', Resource())
