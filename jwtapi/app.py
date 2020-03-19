#! /usr/bin/env python3
'''
Practice to implement JWT authentication/authorization on Falcon API

#Command to start server
#    waitress-serve --port=8000 --call 'jwtapi.app:get_app'

'''
import falcon
from falcon_auth import FalconAuthMiddleware

import jwtapi.app_auth as app_auth
import jwtapi.app_resources as app_resources
#from .app_auth import jwt_auth, Authenticate, RefreshToken, InvalidateToken
#from .app_resources import PublicInfo, PrivateInfo

open_routes = [ '/auth/api/v1/login',
                '/auth/api/v1/refresh',
                '/media/api/v1/public', ]

auth_middleware = FalconAuthMiddleware(app_auth.jwt_auth, exempt_routes=open_routes)

def create_app():
    api = falcon.API(middleware=[auth_middleware])
    api.add_route('/auth/api/v1/login', app_auth.Authenticate())
    api.add_route('/auth/api/v1/refresh', app_auth.RefreshToken())
    api.add_route('/auth/api/v1/invalidate', app_auth.InvalidateToken())
    api.add_route('/media/api/v1/public', app_resources.PublicInfo())
    api.add_route('/media/api/v1/private', app_resources.PrivateInfo())
    return api

def get_app():
    return create_app()
