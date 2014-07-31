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


class RavenResponseError(RavenError):
    pass


class SignatureError(RavenResponseError):
    pass


class AuthenticationError(RavenError):
    pass


class UserCancelledError(RavenAuthenticationError):
    pass