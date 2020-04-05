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


open_routes = ['/api/v1/auth/login',
               '/api/v1/auth/refresh',
               '/api/v1/auth/user-mgmt',
               '/api/v1/media/public', ]

auth_middleware = FalconAuthMiddleware(app_auth.jwt_auth, exempt_routes=open_routes)
db_middleware = SQLAlchemySessionManager(Session)
cors_middleware = app_auth.CORSComponent()


def create_app():
    api = falcon.API(middleware=[auth_middleware, db_middleware, cors_middleware])
    api.add_route('/api/v1/auth/login', app_auth.Login())
    api.add_route('/api/v1/auth/refresh', app_auth.RefreshToken())
    api.add_route('/api/v1/auth/invalidate', app_auth.InvalidateToken())
    api.add_route('/api/v1/auth/user-mgmt', app_auth.UserMgmt())
    api.add_route('/api/v1/media/public', app_resources.PublicInfo())
    api.add_route('/api/v1/media/private', app_resources.PrivateInfo())
    return api


def get_app():
    return create_app()
