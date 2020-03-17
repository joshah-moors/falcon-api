#! /usr/bin/env python3
'''
Starting with:
    https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
'''

from sqlalchemy import create_engine

engine = create_engine('sqlite:///db/backend.db')
