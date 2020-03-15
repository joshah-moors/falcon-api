#! /usr/bin/env python3
'''
Practice to implement JWT authentication/authorization on Falcon API

#Command to start server
#    waitress-serve --port=8000 --call 'falconapi.app:get_app'

'''
import datetime
import json

import falcon
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend

# This is held in the environment somewhere
APP_SECRET = 'Tz#SZ4The0AJU^jB'

class Authenticate:
    def on_post(self, req, resp):
        user_payload = {
            'subject': 'joshah@joshah.com',
            "issuer": "John Snow",
            "expires_at": str(datetime.datetime.utcnow() + datetime.timedelta(hours=10)),
            "issued_at": str(datetime.datetime.utcnow()),
        }
        jwt = jwt_auth.get_auth_token({'test': 'yeah'})
        print(str(jwt))

class PublicInfo:
    def on_get(self, req, resp):
        return_data = {
            'status': 'success',
            'data': 'it\'s all good',
        }
        resp.body = json.dumps(return_data)

class PrivateInfo:
    def on_get(self, req, resp):
        return_data = {
            'status': 'success',
            'data': 'joshah is cool (don\'t tell anyone)',
        }
        resp.body = json.dumps(return_data)

# To implement auth, need a function to verify user
def user_loader (username, password):
    # Business logic to check the db goes here
    return {'username': username}

# JWT Backend & Middleware
jwt_auth = JWTAuthBackend(user_loader, APP_SECRET)
auth_middleware = FalconAuthMiddleware(jwt_auth,
                exempt_routes=['/public', '/login'])

def create_app():
    api = falcon.API(middleware=[auth_middleware])
    api.add_route('/login', Authenticate())
    api.add_route('/public', PublicInfo())
    api.add_route('/private', PrivateInfo())
    return api

def get_app():
    return create_app()
