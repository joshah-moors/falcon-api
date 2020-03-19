#! /usr/bin/env python3
'''
The auth flow described here is taken from this article:
    https://levelup.gitconnected.com/secure-jwts-with-backend-for-frontend-9b7611ad2afb
'''

import json

import falcon
from falcon_auth import JWTAuthBackend

import jwtapi.app_db as app_db

# This is held in the environment somewhere
APP_SECRET = 'Yz#SZ4The0AJU^jC'

# JWT Backend & Middleware
user_loader = lambda token_content: token_content['user']
exp_time = 15 * 60    # 15 mins * 60 seconds
jwt_auth = JWTAuthBackend(user_loader, APP_SECRET, expiration_delta=exp_time)


class Authenticate:
    def on_post(self, req, resp):
        # Parse user/pass out of the body
        username = req.media['username']
        password = req.media['password']
        #print(f'RECEIVED: User: {user} -- Pass: {pw}')
        #
        #
        #   - Refresh token
        #       (Age should be set by user "keep me logged in" king of thing)
        #             30 days
        refresh_age = 30 * 24 * 60 * 60
        #
        #   ~ VERIFY USER LOGIC GOES HERE ~
        #
        #  1. SELECT username, pw_hash, salt from db
        #
        #  2. Re-hash the pw provided by the user with salt from db
        #
        #  3. If newly generated pw hash mathes db:
        #        - Create JWT
        #        - DB log refresh token
        #        - Return JWT & refresh token
        #     If no match:
        #        return a 401 unauthorized
        #
        jwt = jwt_auth.get_auth_token({'username': user})
        resp_dict = {
            'accessToken': jwt,
            'refreshToken': '',
            'refreshAge': refresh_age,
        }
        resp.body = json.dumps(resp_dict)
        resp.status = falcon.HTTP_200


class RefreshToken:
    def on_post(self, req, resp):
        # Parse refreshToken out of body
        refresh_token = req.media['refreshToken']
        #
        # This part will need 2 pieces of data:
        #    - the expired token
        #    - the refresh token
        #
        # First decode the expired token and check the user
        # Then hit the db (seperate table) and see if refresh token is valid for that user
        user = None   # for linting
        #    - update refresh token in DB, and return
        jwt = jwt_auth.get_auth_token({'username': user})
        resp_dict = {
            'accessToken': jwt,
            'refreshToken': '',
            'refreshAge': '',
        }
        resp.body = json.dumps(resp_dict)
        resp.status = falcon.HTTP_200


class InvalidateToken:
    def on_post(self, req, resp):
        #
        # Go to the database, clear the entry for the refresh token
        #
        resp.status = falcon.HTTP_200


class UserMgmt:
    def on_post(self, req, resp):
        email = req.media['email']
        username = req.media['username']
        password = req.media['password']
        #
        session = app_db.Session()
        #
        #    ADD VALIDATIONS
        #         - ensure email doesn't exist in db
        #         - ensure username isn't taken
        #
        #
        this_user = app_db.User(username, app_db.hash_this(password, app_db.SALT), email)
        session.add(this_user)
        #
        session.commit()
        session.close()
        #
        resp_dict = {
            'status': 'success',
        }
        resp.body = json.dumps(resp_dict)
        resp.status = falcon.HTTP_200

