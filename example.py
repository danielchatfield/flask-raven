
from flask import app

from flask_raven import raven_auth


@app.route('/dashboard')
@raven_auth
def dashboard():
    pass

"""
 RAVEN_SESSION_TIMEOUT = 60 * 60 * 24
 RAVEN_SESSION_KEY = "raven"
 RAVEN_USER_CANCELLED = url


 > check if this is a raven request
  - do raven request
 > check if active session
 > if no active session
 > redirect to raven


 do raven request:
    Parse raven response
    do checks
    add to session

"""
