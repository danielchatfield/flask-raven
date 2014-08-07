# -*- coding: utf-8 -*-
"""
    flask_raven.errors
    ~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Daniel Chatfield
    :license: Artistic 2.0
"""


class RavenError(Exception):
    """ The base error for all flask_raven errors """
    pass


class ResponseError(RavenError):
    pass


class SignatureError(ResponseError):
    pass


class TimestampError(ResponseError):
    pass


class UrlError(ResponseError):
    pass


class AuthenticationError(RavenError):
    pass


class UserCancelledError(AuthenticationError):
    pass
