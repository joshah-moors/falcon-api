#! /usr/bin/env python3

import falcon
import falcon.testing

import jwtapi.app_auth as app_auth



#class InvalidateToken:
#    def on_post(self, req, resp):
#        user_id = req.context['user']['id']
#        req.context['db_session'].query(app_db.RefreshToken)   \
#               .filter(app_db.RefreshToken.user_id == user_id) \
#               .delete()
#        req.context['db_session'].commit()
#        resp.status = falcon.HTTP_200
#
#
def test_invalidate_post():
    #
    #env = falcon.testing.create_environ()
    #req = falcon.request.Request(env, email='joshah@fakemail.com')
    #resp = falcon.Response()
    #
    #r = app_auth.UserMgmt().on_post(req, resp)
    ##req = falcon.testing.helpers.create_req()
    pass


