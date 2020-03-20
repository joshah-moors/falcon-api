#! /usr/bin/env python3
'''
The auth flow described here is taken from this article:
    https://levelup.gitconnected.com/secure-jwts-with-backend-for-frontend-9b7611ad2afb
'''

import json
import uuid

import falcon
import jwt
from falcon_auth import JWTAuthBackend
from sqlalchemy import or_

import jwtapi.app_db as app_db
from jwtapi.app_db import User

# This is held in the environment somewhere
APP_SECRET = 'Yz#SZ4The0AJU^jC'

# JWT Backend & Middleware
user_loader = lambda token_content: token_content['user']
jwt_exp_time = 15 * 60    # 15 mins * 60 seconds
jwt_auth = JWTAuthBackend(user_loader, APP_SECRET, expiration_delta=jwt_exp_time)
refresh_exp_time = 30 * 24 * 60 * 60
refresh_auth = JWTAuthBackend(user_loader, APP_SECRET, expiration_delta=refresh_exp_time)


class Authenticate:
    def on_post(self, req, resp):
        # Parse user/pass out of the body
        username = req.media['username']
        password = req.media['password']
        #  VERIFY USER LOGIC GOES HERE:
        #  1. SELECT username, pw_hash, salt from db
        session = app_db.Session()
        user_result = session.query(User)                                                    \
                             .filter(or_(User.username == username, User.email == username)) \
                             .all()
        if len(user_result) == 0:
            # No match
            user_not_found_dict = {'status': 'user not found'}
            resp.body = json.dumps(user_not_found_dict)
            resp.status = falcon.HTTP_409
            return
        #
        #  2. Re-hash the pw provided by the user with salt from db
        pw_hash = app_db.hash_this(password, app_db.SALT)
        #
        #  3. If newly generated pw hash mathes db:
        #        - Create JWT, DB log refresh token, return JWT and refresh token
        for user in user_result:
            if pw_hash == user.passhash:
                jwt = jwt_auth.get_auth_token({'username': user.username})
                #
                #
                #    CREATE REFRESH TOKEN SHOULD BE WRAPPED IN INPUT OF
                #                     "Keep me logged in option"
                #
                #
                # Create a refresh token secret
                refresh_secret = str(uuid.uuid4())
                # Log refresh secret in the db -- delete if exists first
                session.query(app_db.RefreshToken)                     \
                       .filter(app_db.RefreshToken.user_id == user.id) \
                       .delete(synchronize_session=False)
                session.add(app_db.RefreshToken(user.username, refresh_secret, user))
                session.commit()
                # Create a refresh token
                refresh_token = refresh_auth.get_auth_token({
                        'username': user.username,
                        'refresh': refresh_secret
                    })
                # Return everything in the response
                resp_dict = {
                    'accessToken': jwt,
                    'refreshToken': refresh_token,
                    'refreshAge': refresh_exp_time,
                }
                resp.body = json.dumps(resp_dict)
                resp.status = falcon.HTTP_200
                return
        # If no match: return a 401 unauthorized
        resp.status = falcon.HTTP_401


class RefreshToken:
    def on_post(self, req, resp):
        # Parse refreshToken out of body
        refresh_token = req.media['refreshToken']
        # Verify refresh token sent in body
        try:
            payload = jwt.decode(jwt=refresh_token, 
                                 key=refresh_auth.secret_key,
                                 options=refresh_auth.options,
                                 algorithms=[refresh_auth.algorithm],
                                 issuer=refresh_auth.issuer,
                                 audience=refresh_auth.audience,
                                 leeway=refresh_auth.leeway)
        #except jwt.InvalidTokenError as ex:
        #    raise falcon.HTTPUnauthorized(
        #        description=str(ex))
        except Exception as ex:
            raise falcon.HTTPUnauthorized(description=str(ex))
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
        session = app_db.Session()
        # Ensure username doesn't exist in db
        user_result = session.query(User)                       \
                             .filter(User.username == username) \
                             .all()
        if len(user_result) > 0:
            user_taken_dict = {'status': 'username taken'}
            resp.body = json.dumps(user_taken_dict)
            resp.status = falcon.HTTP_409
            return
        # Ensure email doesn't exist in db
        email_result = session.query(User)                 \
                              .filter(User.email == email) \
                              .all()
        if len(email_result) > 0:
            email_taken_dict = {'status': 'email taken'}
            resp.body = json.dumps(email_taken_dict)
            resp.status = falcon.HTTP_409
            return
        # Good to create user
        this_user = User(username, app_db.hash_this(password, app_db.SALT), email)
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
