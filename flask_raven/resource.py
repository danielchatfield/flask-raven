# -*- coding: utf-8 -*-
"""
    flask_raven.resource
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Daniel Chatfield
    :license: Artistic 2.0
"""

from datetime import datetime

from flask import request

from .errors import (RavenAuthenticationError, RavenResponseError,
                     SignatureError, UserCancelledError)
from .helpers import get_config, b64decode

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


__all__ = ['RavenResponse', 'RavenRequest']


class RavenResponse(object):
    """ Class representing the response from raven """

    _response_fields = ("ver", "status", "msg", "issue", "id", "url",
                        "principal", "ptags", "auth", "sso", "life", "params",
                        "kid", "sig")

    def __init__(self, response):
        """ Parses a string response and returns a RavenResponse object
        or throws an exception if something went wrong.
        """
        values = self._split_response(response)

        for key, value in zip(self._response_fields, values):
            setattr(self, key, value)

        self.issue = datetime.strptime(self.issue, "%Y%m%dT%H%M%SZ")

        self.status = int(self.status)

        self.sig = (
            self.sig.replace('-', '+').replace('.', '/').replace('_', '='))

        try:
            self.sig = b64decode(self.sig, validate=True)
        except (TypeError, ValueError):
            raise SignatureError('Signature was malformed')

        self.check_signature()

        if self.status == 410:
            raise UserCancelledError()
        elif self.status != 200:
            raise RavenAuthenticationError()

    def _split_response(self, response_string):
        values = response_string.split('!')

        if len(values) != len(self._response_fields):
            raise RavenResponseError(
                "Incorrect number of response fields, expecting %d but got %d"
                % (len(self._response_fields), len(values)))

        return values

    def check_signature():
        pass


class RavenRequest(object):
    """ Class representing a request to the raven server """
    def __init__(self, url=None):

        if url is None:
            url = request.url

        self.ver = 3
        self.url = url

    @property
    def url(self):

        params = {
            'ver': self.ver,
            'url': self.url
        }

        return get_config('auth_endpoint') + '?' + urlencode(params)
