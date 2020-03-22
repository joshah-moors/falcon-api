#! /usr/bin/env python3
'''
Starting with:
    https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
'''
import datetime
import hashlib
import os
import uuid

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, func, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

SALT = b'\xd6\xea\xc1A\xf3!\xce\xc7\xa6\xec\x93\xec\xcc_{,\x08\x9aWK\xb2R\xc4\x08\xa8\xa1@\xf6\x07\x7fe\xea'

engine = create_engine('sqlite:///jwtapi/db/backend.db')
#engine = create_engine('sqlite:///db/backend.db')
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


def hash_this(secret, salt):
    return hashlib.pbkdf2_hmac(
        'sha256',   # hash digest algorithm
        secret.encode('utf-8'),
        salt,
        100_000
    )


if __name__ == '__main__':
    # Create the tables
    #Base.metadata.create_all(engine)
    ''' 
    # Insert some records
    session = Session()

    # Create objects
    users, user_dict = [
        ('texasLonghorn', hash_this('ut4Ever', SALT), 'txlonghorn@gmail.com'),
        ('SonnySideUp', hash_this('this_hash', SALT), 'mrno20@yahoo.com'),
        ('whereareyoufish', hash_this('some*passw0rd', SALT), 'whereisthatfish@gmail.com'),
    ], {}
    for user in users:
        user_dict[user[0]] = Users(*user)

    refresh_tokens, token_dict = [
        ('texasLonghorn', str(uuid.uuid4()), user_dict['texasLonghorn']),
        ('SonnySideUp', str(uuid.uuid4()), user_dict['SonnySideUp']),
        ('whereareyoufish', str(uuid.uuid4()), user_dict['whereareyoufish']),
    ], {}
    for token in refresh_tokens:
        token_dict[token[0]] = RefreshTokens(*token)
    
    # Insert the records

    #print(user_dict)
    for user in user_dict.values():
        session.add(user)

    #print(token_dict)
    for token in token_dict.values():
        session.add(token)

    # Commit & close session
    #session.commit()
    #session.close()
    
    # To Query

    session = Session()

    #user_results = session.query(Users).all()
    #
    #user_result = session.query(Users) \
    #    .filter(Users.username.ilike('S%'))
    #
    #user_result = session.query(Users) \
    #    .join(RefreshTokens) \
    #    .filter(Users.username == 'texasLonghorn') \
    #    .all()
    #
    user_result = session.query(RefreshTokens) \
        .filter(RefreshTokens.create_ts > datetime.date(2020, 3, 20))
    for user in user_result:
        #print(dir(user))
        print(f'Token secrest for user {user.user_id} is: {user.token_secret}')
    
    # Join tables
    session = Session()
    user_results = session.query(User).join(RefreshToken)  \
                          .filter(User.username == 'texasLonghorn') \
                          .all()
    print(user_results)
    print(dir(user_results[0]))
    for user in user_results:
        print(user.username, user.refresh_token.token_secret)
    '''
    pass