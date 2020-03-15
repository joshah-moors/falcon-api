#! /usr/bin/env python3
'''
Practice to implement JWT authentication/authorization on Falcon API

#Command to start server
#    waitress-serve --port=8000 --call 'falconapi.app:get_app'

'''
import falcon
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend

from .app_functions import *

# This is held in the environment somewhere
APP_SECRET = 'Yz#SZ4The0AJU^jC'

class Authenticate:
    def on_post(self, req, resp):
        # Parse user/pass out of the body
        user = req.media['user']
        pw = req.media['password']
        #print(f'RECEIVED: User: {user} -- Pass: {pw}')
        #
        #   ~ VERIFY USER LOGIC GOES HERE ~
        #
        jwt = jwt_auth.get_auth_token({'username': user})
        resp_dict = {
            'accessToken': jwt,
            'refreshToken': '',
            'refreshAge': '',
        }
        resp.body = json.dumps(resp_dict)
        resp.status = falcon.HTTP_200

# JWT Backend & Middleware
user_loader = lambda token_content: token_content['user']
jwt_auth = JWTAuthBackend(user_loader, APP_SECRET)
auth_middleware = FalconAuthMiddleware(jwt_auth,
                exempt_routes=[
                                '/auth/api/v1/login',
                                '/public',
                              ])

def create_app():
    api = falcon.API(middleware=[auth_middleware])
    api.add_route('/auth/api/v1/login', Authenticate())
    api.add_route('/public', PublicInfo())
    api.add_route('/private', PrivateInfo())
    return api

def get_app():
    return create_app()
