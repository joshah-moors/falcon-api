# falcon-jwt-api
Falcon REST API with JWT Authentication & refresh tokens - SQLAlchemy/SQLite

## Description
Creating a backend for a Node.js based frontend. This project implements JWT (JSON Web Tokens) to authorize frontend requests to API resources.

The design was taken from Szabolcs Gelencser's article '[JWT Architecture for Modern Apps](https://levelup.gitconnected.com/secure-jwts-with-backend-for-frontend-9b7611ad2afb).'


The JWT Authorization is using [falcon-auth](https://falcon-auth.readthedocs.io/en/latest/readme.html) package.


## Usage
This is an implementation of the falcon-auth package that uses short-lived JWTs and extends the functionality by setting a long-term refresh token that can be used to generate new access tokens. The lifespan of these tokens in set in env.py:

```
# Access Token:    15 mins * 60 seconds
EXP_ACCESS_TOKEN = 15 * 60

# Refresh Token:    7 days
EXP_REFRESH_TOKEN = 7 * 24 * 60 * 60
```

The refresh token inserts a secret value associated with the user in the db - subsequent session refreshes validate the refresh JWT and confirm the secret value.

An '/invalidate' endpoint is included to delete the secret value in the db and disallow further use of the refresh token.

This is a trivial example that uses SQLite for the database. SQLalchemy is used to build the db model and DML actions, conversion to a relational database could be easily configured in env.py.

## Tests
Unit tests are included in the `tests` directory. Use `pytest` in the root directory to execute unit tests.

An integration test script (pytest) is also included in the `tests` directory.

## Contributions
Feel free to fork this repo and/or submit pull requests for enhancements!~