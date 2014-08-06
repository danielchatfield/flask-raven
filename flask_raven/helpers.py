# -*- coding: utf-8 -*-
"""
    flask_raven.helpers
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Daniel Chatfield
    :license: Artistic 2.0
"""

import base64
from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs

from flask import current_app, request

import config
import keys


def is_auth_request():
    return 'WLS-Response' in request.args


def get_config(key, default=None):

    if default is None and key.upper() in dir(config):
        default = getattr(config, key.upper())

    return current_app.config.get(key, default)


def get_key():
    """ Returns the public key used to check signatures specified by RAVEN_KEY.

        If RAVEN_KEY is not defined then the key to use is decided by:

        If RAVEN_TEST is False (the default) then the LIVE_KEY is used, if it
        is True then the TEST_KEY is used.
    """

    key = get_config('key')

    if key:
        return key

    if get_config('test', False):
        raise NotImplementedError("Test key is not implemented")
    else:
        return keys.LIVE_KEY


def b64decode(value, validate):
    result = base64.b64decode(value)

    if validate and base64.b64encode(result) != value:
        raise ValueError('String failed validation')

    return result


def remove_query_arg(arg='WLS-Response', url=None):
    if url is None:
        url = request.url
    u = urlparse(url)
    query = parse_qs(u.query)
    query.pop(arg, None)
    u = u._replace(query=urlencode(query, True))
    return urlunparse(u)
