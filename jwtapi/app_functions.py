#! /usr/bin/env python3

import json

import falcon
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend


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


class PublicInfo:
    def on_get(self, req, resp):
        return_data = {
            'status': 'success',
            'data': 'it\'s all good',
        }
        resp.body = json.dumps(return_data)


class PrivateInfo:
    def on_get(self, req, resp):
        # Verify Authentication added user to request context
        print(f'Token Showed User Logged in is: {req.context}')
        #
        return_data = {
            'status': 'success',
            'data': 'joshah is cool (don\'t tell anyone)',
        }
        resp.body = json.dumps(return_data)
