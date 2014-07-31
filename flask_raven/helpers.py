# -*- coding: utf-8 -*-
"""
    flask_raven.helpers
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Daniel Chatfield
    :license: Artistic 2.0
"""

import base64

from flask import current_app, request

import flask_raven.config as config


def is_auth_request():
    return 'WLS-Response' in request.args


def get_config(key, default=None):

    if default is None and key.upper() in dir(config):
        default = getattr(config, key.upper())

    return current_app.get_namespce('RAVEN_').get(key, default)


def b64decode(value, validate):
    result = base64.b64decode(value)

    if validate and base64.b64encode(result) != value:
        raise ValueError('String failed validation')

    return result
