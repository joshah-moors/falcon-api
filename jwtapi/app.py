#! /usr/bin/env python3
'''
Practice to implement JWT authentication/authorization on Falcon API

#Command to start server
#    waitress-serve --port=8000 --call 'jwtapi.app:get_app'

'''
import falcon
from falcon_auth import FalconAuthMiddleware

from .app_auth import jwt_auth, Authenticate, Refresh, Invalidate
from .app_resources import PublicInfo, PrivateInfo

open_routes = [ '/auth/api/v1/login',
                '/auth/api/v1/refresh',
                '/public', ]

auth_middleware = FalconAuthMiddleware(jwt_auth, exempt_routes=open_routes)

def create_app():
    api = falcon.API(middleware=[auth_middleware])
    api.add_route('/auth/api/v1/login', Authenticate())
    api.add_route('/auth/api/v1/refresh', Refresh())
    api.add_route('/auth/api/v1/invalidate', Invalidate())
    api.add_route('/public', PublicInfo())
    api.add_route('/private', PrivateInfo())
    return api

def get_app():
    return create_app()
