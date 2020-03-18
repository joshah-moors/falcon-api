#! /usr/bin/env python3
'''
Starting with:
    https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db/backend.db')
Session = sessionmaker(bind=engine)

Base = declarative_base()


