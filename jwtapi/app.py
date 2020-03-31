#! /usr/bin/env python3
'''
Falcon API implementing JWT auth

Command to start server (from repo root dir)
    waitress-serve --port=8000 --call 'jwtapi.app:get_app'
'''

import falcon
from falcon_auth import FalconAuthMiddleware

import jwtapi.app_auth as app_auth
import jwtapi.app_resources as app_resources
from jwtapi.app_db import Session, SQLAlchemySessionManager


open_routes = ['/auth/api/v1/login',
               '/auth/api/v1/refresh',
               '/auth/api/v1/user-mgmt',
               '/media/api/v1/public', ]

auth_middleware = FalconAuthMiddleware(app_auth.jwt_auth, exempt_routes=open_routes)
db_middleware = SQLAlchemySessionManager(Session)
cors_middleware = app_auth.CORSComponent()


def create_app():
    api = falcon.API(middleware=[auth_middleware, db_middleware, cors_middleware])
    api.add_route('/auth/api/v1/login', app_auth.Login())
    api.add_route('/auth/api/v1/refresh', app_auth.RefreshToken())
    api.add_route('/auth/api/v1/invalidate', app_auth.InvalidateToken())
    api.add_route('/auth/api/v1/user-mgmt', app_auth.UserMgmt())
    api.add_route('/media/api/v1/public', app_resources.PublicInfo())
    api.add_route('/media/api/v1/private', app_resources.PrivateInfo())
    return api


def get_app():
    return create_app()
