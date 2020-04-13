#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
My first time using SQLAlchemy, starting with:
    https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
'''

import datetime
import hashlib

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

import jwtapi.env as ENV

SALT = b'\xd6\xea\xc1A\xf3!\xce\xc7\xa6\xec\x93\xec\xcc_{,\x08\x9aWK\xb2R\xc4\x08\xa8\xa1@\xf6\x07\x7fe\xea'

engine = create_engine(f'sqlite:///{ENV.DB_PATH}')
Session = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    passhash = Column(String)
    email = Column(String)

    def __init__(self, username, passhash, email):
        self.username = username
        self.passhash = passhash
        self.email = email

    def create(self) -> (bool, str):
        session = Session()
        # Ensure username doesn't exist in db
        user_res = session.query(User)                                                    \
                          .filter(func.upper(User.username) == func.upper(self.username)) \
                          .all()
        if len(user_res) > 0:
            return False, 'username taken'
        # Ensure email doesn't exist in db
        email_res = session.query(User)                                              \
                           .filter(func.upper(User.email) == func.upper(self.email)) \
                           .all()
        if len(email_res) > 0:
            return False, 'email taken'
        # Good to create user
        session.add(self)
        session.commit()
        session.close()
        return True, 'success'


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    token_secret = Column(String)
    create_ts = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", backref=backref("refresh_token", uselist=False))

    def __init__(self, user_id, token_secret, user):
        self.user_id = user_id
        self.token_secret = token_secret
        self.user = user

class UserHelpers:
    def find_by_username_or_email(self, username):
        session = Session()
        
        res = session.query(User)                                                    \
                     .filter(or_(User.username == username, User.email == username)) \
                     .all()

        session.close()
        return res


class SQLAlchemySessionManager:
    ''' Create a session for every request, close it when the request ends '''
    def __init__(self, Session):
        self.db_session = Session

    def process_resource(self, req, resp, resource, params):
        if req.method == 'OPTIONS':
            return
        req.context['db_session'] = self.db_session()

    def process_response(self, req, resp, resource, req_succeeded):
        if req.method == 'OPTIONS':
            return
        if req.context.get('db_session'):
            if not req_succeeded:
                req.context['db_session'].rollback()
            req.context['db_session'].close()


def hash_this(secret, salt):
    return hashlib.pbkdf2_hmac(
        'sha256',   # hash digest algorithm
        secret.encode('utf-8'),
        salt,
        100_000
    )
