# -*- coding: utf-8 -*-
"""
    flask_raven.resource
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Daniel Chatfield
    :license: Artistic 2.0
"""

from datetime import datetime

from flask import request

from Crypto.Hash.SHA import SHA1Hash
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from .errors import (AuthenticationError, ResponseError, SignatureError,
                     TimestampError, UrlError, UserCancelledError)
from .helpers import get_config, get_key, b64decode, remove_query_arg

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


__all__ = ['RavenResponse', 'RavenRequest']


class RavenResponse(object):
    """ Class representing the response from raven

    The response fields and their associated values are:

    Field     Value
    --------- ---------------------------------------------------------------

    ver       [REQUIRED] The version of the WLS protocol in use. This document
              describes versions 1, 2 and 3 of the protocol. This will not be
              greater than the 'ver' parameter supplied in the request

    status    [REQUIRED] A three digit status code indicating the status of
              the authentication request. '200' indicates success, other
              possible values are listed below.

    msg       [OPTIONAL] A text message further describing the status of the
              authentication request, suitable for display to end-user.

    issue     [REQUIRED] The date and time that this authentication response
              was created.

    id        [REQUIRED] An identifier for this response. 'id', combined
              with 'issue' provides a unique identifier for this
              response. 'id' is not unguessable.

    url       [REQUIRED] The value of 'url' supplied in the 'authentication
              request' and used to form the 'authentication response'.

    principal [REQUIRED if status is '200', otherwise required to be
              empty] If present, indicates the authenticated identity of
              the browser user

    ptags     [OPTIONAL in a version 3 response, MUST be entirely
              omitted otherwise] A potentially empty sequence of text
              tokens separated by ',' indicating attributes or
              properties of the identified principal. Possible values of
              this tag are not standardised and are a matter for local
              definition by individual WLS operators (see note
              below). WAA SOULD ignore values that they do not
              recognise.

    auth      [REQUIRED if authentication was successfully established by
              interaction with the user, otherwise required to be empty]
              This indicates which authentication type was used. This
              value consists of a single text token as described below.

    sso       [REQUIRED if 'auth' is empty] Authentication must have been
              established based on previous successful authentication
              interaction(s) with the user.  This indicates which
              authentication types were used on these occasions. This
              value consists of a sequence of text tokens as described
              below, separated by ','.

    life      [OPTIONAL] If the user has established an authenticated
              'session' with the WLS, this indicates the remaining life
              (in seconds) of that session. If present, a WAA SHOULD use
              this to establish an upper limit to the lifetime of any
              session that it establishes.

    params    [REQUIRED to be a copy of the params parameter from the
              request]

    kid       [REQUIRED if a signature is present] A string which identifies
              the RSA key which will be used to form a signature
              supplied with the response. Typically these will be small
              integers.

    sig       [REQUIRED if status is 200, OPTIONAL otherwise] A public-key
              signature of the response data constructed from the entire
              parameter value except 'kid' and 'signature' (and their
              separating ':' characters) using the private key
              identified by 'kid', the SHA-1 hash algorithm and the
              'RSASSA-PKCS1-v1_5' scheme as specified in PKCS #1 v2.1
              [RFC 3447] and the resulting signature encoded using the
              base64 scheme [RFC 1521] except that the characters '+',
              '/', and '=' are replaced by '-', '.' and '_' to reduce
              the URL-encoding overhead.
    """

    _response_fields = ("ver", "status", "msg", "issue", "id", "url",
                        "principal", "ptags", "auth", "sso", "life", "params",
                        "kid", "sig")

    def __init__(self, response):
        """ Parses a string response and returns a RavenResponse object
        or throws an exception if something went wrong.
        """
        self.raw_response = response

        values = self._split_response(response)

        # Strip the kid and sig to obtain the payload used to generate the
        # signature
        self.payload = '!'.join(values[:-2])

        for key, value in zip(self._response_fields, values):
            setattr(self, key, value)

        self.issue = datetime.strptime(self.issue, "%Y%m%dT%H%M%SZ")

        self.status = int(self.status)

        replace = {
            '-': '+',
            '.': '/',
            '_': '='
        }

        for search, replace_with in replace.iteritems():
            self.sig = self.sig.replace(search, replace_with)

        try:
            self.sig = b64decode(self.sig, validate=True)
        except (TypeError, ValueError):
            raise SignatureError('Signature was malformed')

        self.check_request_url()
        self.check_timestamp()
        self.check_signature()

        if self.status == 410:
            raise UserCancelledError()
        elif self.status != 200:
            raise AuthenticationError()

    def _split_response(self, response_string):
        values = response_string.split('!')

        if len(values) != len(self._response_fields):
            raise ResponseError(
                "Incorrect number of response fields, expecting %d but got %d"
                % (len(self._response_fields), len(values)))

        return values

    def check_request_url(self):
        if self.url != remove_query_arg():
            raise UrlError(
                "The requested url does not match the url returned by raven")

    def check_timestamp(self):
        now = datetime.utcnow()
        diff = now - self.issue

        if diff.seconds > get_config('RAVEN_RESPONSE_TIMESTAMP_DIFF'):
            raise TimestampError(
                "Too much time has elapsed since this auth request was made")

    def check_signature(self):
        key = RSA.importKey(get_key())
        mhash = SHA1Hash(self.payload)
        verifier = PKCS1_v1_5.new(key)

        if not verifier.verify(mhash, self.sig):
            raise SignatureError(
                "Signature mismatch - response has been tampered with")


class RavenRequest(object):
    """ Class representing a request to the raven server """
    def __init__(self, url=None):

        if url is None:
            url = request.url

        self.ver = 3
        self.url = url

    @property
    def redirect_url(self):

        params = {
            'ver': self.ver,
            'url': self.url
        }

        return get_config('RAVEN_AUTH_ENDPOINT') + '?' + urlencode(params)
