#! /usr/bin/env python3

import json


class PublicInfo:
    def on_get(self, req, resp):
        return_data = {
            'status': 'success',
            'data': 'it\'s all good',
        }
        resp.body = json.dumps(return_data)


class PrivateInfo:
    def on_get(self, req, resp):
        current_user = req.context['user']['username']
        return_data = {
            'status': 'success',
            'data': 'joshah is cool (don\'t tell anyone)',
            'context': f'this data was produced for: {current_user}'
        }
        resp.body = json.dumps(return_data)
