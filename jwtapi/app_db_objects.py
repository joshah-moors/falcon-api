# coding=utf-8

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from base import base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    passhash = Column(String)
    email = Column(String)

    def __init__(self, username, passhash, email):
        self.username = username
        self.passhash = passhash
        self.email = email


class RefreshTokens(Base):
    __tablename__ = 'refresh_tokens'
    
    token_secret = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users", backref=backref("refresh_token", uselist=False))

    def __init__(self, token_secret, user):
        self.token_secret = token_secret
        self.user = user

