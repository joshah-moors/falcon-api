import json

import falcon
import msgpack

class Resource:

    def on_get(self, req, resp):
        doc = {
            'images': [
                {
                    'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
                }

            ]
        }

        # Create a JSON representation of the resource
        #resp.body = json.dumps(doc, ensure_ascii=False)
        #
        # Give Message Pack a shot
        resp.data = msgpack.packb(doc, use_bin_type=True)
        resp.content_type = falcon.MEDIA_MSGPACK
        #
        # 200 is default
        resp.status = falcon.HTTP_200
