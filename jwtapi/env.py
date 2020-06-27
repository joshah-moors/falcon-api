# -*- coding: UTF-8 -*-

# In production - hold these in env variables
APP_SECRET = '__some_app_secret__'
SALT = b'\xd6\xea\xc1A\xf3!\xce\xc7\xa6\xec\x93\xec\xcc_{,\x08\x9aWK\xb2R\xc4\x08\xa8\xa1@\xf6\x07\x7fe\xea'

# In production - replace with DB Connection
DB_PATH = 'c:/Users/Joshah/Desktop/Git Repo/falcon-jwt-api/jwtapi/db/backend.db'

# Access Token:    15 mins * 60 seconds
EXP_ACCESS_TOKEN = 15 * 60

# Refresh Token:    7 days
EXP_REFRESH_TOKEN = 7 * 24 * 60 * 60

# CORS Max Age:    24 hours
CORS_MAX_AGE = str(24 * 60 * 60)

# Flag for secure cookies
RUNNING_IN_PROD = False
