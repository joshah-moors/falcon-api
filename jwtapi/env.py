# -*- coding: UTF-8 -*-

# In production - this is held in an environment varaible
APP_SECRET = '__some_app_secret__'

# In production - replace with DB Connection
DB_PATH = 'c:/Users/Joshah/Desktop/Git Repo/falcon-jwt-api/jwtapi/db/backend.db'

# Access Token:    15 mins * 60 seconds
EXP_ACCESS_TOKEN = 15 * 60

# Refresh Token:    7 days
EXP_REFRESH_TOKEN = 7 * 24 * 60 * 60

# Flag for secure cookies
RUNNING_IN_PROD = False