#! /usr/bin/env python3

import json

import falcon

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
