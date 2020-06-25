#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
This module is a copy of app_auth that will implement cookies in the responses to set the JWT on the front-end
"""

import json
import uuid

import falcon
import jwt as jwt_lib
from falcon_auth import JWTAuthBackend
from sqlalchemy import or_

import jwtapi.app_db as app_db
import jwtapi.env as ENV
from jwtapi.app_db import User, find_user

# JWT Backends
user_loader = lambda token_content: token_content['user']
jwt_auth = JWTAuthBackend(user_loader, ENV.APP_SECRET, expiration_delta=ENV.EXP_ACCESS_TOKEN)
refresh_auth = JWTAuthBackend(user_loader, ENV.APP_SECRET, expiration_delta=ENV.EXP_REFRESH_TOKEN)


class Login2:
    def on_post(self, req, resp):
        if req.media is None:
            resp.body = json.dumps({'status': 'missing username/password'})
            resp.status = falcon.HTTP_409
            return

        if any(('username' not in req.media, 'password' not in req.media)):
            resp.body = json.dumps({'status': 'missing username/password'})
            resp.status = falcon.HTTP_409
            return

        username, password = req.media['username'], req.media['password']
        dbs = req.context['db_session']

        # Ensure user exists
        #user_result = dbs.query(User)                                                    \
        #                 .filter(or_(User.username == username, User.email == username)) \
        #                 .all()
        user_result = find_user(dbs, username)
        if len(user_result) == 0:
            resp.body = json.dumps({'status': 'user not found'})
            resp.status = falcon.HTTP_409
            return

        # Hash the user-provided password
        pw_hash = app_db.hash_this(password, app_db.SALT)

        # If newly generated pw hash mathes db:
        #        - Create JWT, DB log refresh token, return JWT and refresh token
        for user in user_result:
            if pw_hash == user.passhash:
                jwt = jwt_auth.get_auth_token({
                    'username': user.username,
                    'id': user.id
                    })
                # Create a refresh token secret
                refresh_secret = str(uuid.uuid4())
                # Log refresh secret in the db -- delete if exists first
                dbs.query(app_db.RefreshToken)                     \
                   .filter(app_db.RefreshToken.user_id == user.id) \
                   .delete(synchronize_session=False)
                dbs.add(app_db.RefreshToken(user.username, refresh_secret, user))
                dbs.commit()
                # Create a refresh token
                refresh_token = refresh_auth.get_auth_token({
                        'username': user.username,
                        'id': user.id,
                        'refresh': refresh_secret
                    })

                # Assemble response
                resp_dict = {
                    'accessToken': jwt,
                    'refreshToken': refresh_token,
                    'refreshAge': ENV.EXP_REFRESH_TOKEN,
                }
                resp.body = json.dumps(resp_dict)
                resp.status = falcon.HTTP_200
                return
        # If no match: return a 401 unauthorized
        resp.status = falcon.HTTP_401


class RefreshToken2:
    def __init__(self):
        self.claim_opts = dict(('verify_' + claim, True) for claim in refresh_auth.verify_claims)
        self.claim_opts.update(
            dict(('require_' + claim, True) for claim in refresh_auth.required_claims)
        )

    def on_post(self, req, resp):
        if req.media is None:
            resp.status = falcon.HTTP_401
            return

        if 'refreshToken' not in req.media:
            resp.status = falcon.HTTP_401
            return

        refresh_token = req.media['refreshToken']
        # Verify refresh token
        try:
            payload = jwt_lib.decode(jwt=refresh_token,
                                     key=refresh_auth.secret_key,
                                     options=self.claim_opts,
                                     algorithms=[refresh_auth.algorithm],
                                     issuer=refresh_auth.issuer,
                                     audience=refresh_auth.audience,
                                     leeway=refresh_auth.leeway)
        except jwt_lib.InvalidTokenError as ex:
            raise falcon.HTTPUnauthorized(description=str(ex))
        #print(payload)

        this_user = payload['user']['username']
        this_refresh_secret = payload['user']['refresh']

        dbs = req.context['db_session']
        user_result = dbs.query(User).join(app_db.RefreshToken)     \
                         .filter(User.username == this_user)        \
                         .all()
        # Ensure user was found
        if len(user_result) == 0:
            user_not_found_dict = {'status': 'user/token not found'}
            resp.body = json.dumps(user_not_found_dict)
            resp.status = falcon.HTTP_409
            return
        # Check the token secret
        if this_refresh_secret != user_result[0].refresh_token.token_secret:
            resp.status = falcon.HTTP_401
            return
        user_id = user_result[0].id
        dbs.commit()

        user_result = dbs.query(User)                 \
                         .filter(User.id == user_id)  \
                         .all()
        # Create a refresh token secret
        refresh_secret = str(uuid.uuid4())
        # Log refresh secret in the db -- delete if exists
        dbs.query(app_db.RefreshToken)                               \
           .filter(app_db.RefreshToken.user_id == user_result[0].id) \
           .delete()
        dbs.add(app_db.RefreshToken(user_result[0].id, refresh_secret, user_result[0]))
        dbs.commit()

        # Create tokens
        jwt = jwt_auth.get_auth_token({
            'username': this_user,
            'id': user_id
            })

        refresh_token = refresh_auth.get_auth_token({
                'username': this_user,
                'id': user_id,
                'refresh': refresh_secret
            })

        resp_dict = {
            'accessToken': jwt,
            'refreshToken': refresh_token,
            'refreshAge': ENV.EXP_REFRESH_TOKEN,
        }
        resp.body = json.dumps(resp_dict)
        resp.status = falcon.HTTP_200


class InvalidateToken2:
    def on_post(self, req, resp):
        #
        # And unset Cookie here
        #
        user_id = req.context['user']['id']
        req.context['db_session'].query(app_db.RefreshToken)   \
               .filter(app_db.RefreshToken.user_id == user_id) \
               .delete()
        req.context['db_session'].commit()
        resp.status = falcon.HTTP_200


class UserMgmt2:
    def on_post(self, req, resp):
        email = req.media['email']
        username = req.media['username']
        password = req.media['password']
        #
        new_user = User(username, app_db.hash_this(password, app_db.SALT), email)
        crt_status, crt_msg = new_user.create()
        if crt_status is False:
            resp.body = json.dumps({'status': crt_msg})
            resp.status = falcon.HTTP_409
            return
        resp.body = json.dumps({'status': 'success'})
        resp.status = falcon.HTTP_200


