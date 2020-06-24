#! /usr/bin/env python3
'''
Falcon API implementing JWT auth

Command to start server (from repo root dir)
    waitress-serve --port=8000 --call 'jwtapi.app:get_app'
'''

import falcon
from falcon_auth import FalconAuthMiddleware

import jwtapi.env as ENV
import jwtapi.app_auth as app_auth
import jwtapi.app_auth_2 as app_auth_2
import jwtapi.app_resources as app_resources
from jwtapi.app_db import Session, SQLAlchemySessionManager


open_routes = ['/api/v1/auth/login',
               '/api/v1/auth/refresh',
               '/api/v1/auth/user-mgmt',
               '/api/v1/media/public',
               '/api/v2/auth/login',
               '/api/v2/media/public', ]

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
    # v2 cookie routes
    api.add_route('/api/v2/auth/login', app_auth_2.Login2())
    api.add_route('/api/v2/auth/refresh', app_auth_2.RefreshToken2())
    api.add_route('/api/v2/auth/invalidate', app_auth_2.InvalidateToken2())
    api.add_route('/api/v2/auth/user-mgmt', app_auth_2.UserMgmt2())
    api.add_route('/api/v2/media/public', app_resources.PublicInfo())
    # Secure cookies (http/https)
    api.resp_options.secure_cookies_by_default = ENV.RUNNING_IN_PROD
    #
    return api


def get_app():
    return create_app()
