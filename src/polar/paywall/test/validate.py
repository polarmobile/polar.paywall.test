#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012, Polar Mobile.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name Polar Mobile nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL POLAR MOBILE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from polar.paywall.test.schemas import (VALIDATE_SCHEMAS, ERROR_SCHEMAS,
    AUTH_SCHEMAS)

from polar.paywall.test.subcommand import Subcommand

from logging import info, error

# Used to get a session key.
from auth import Auth

import socket


class Validate(Subcommand):
    '''
    Called by the validate subcommand in main.
    '''
    def run(self, arguments):
        '''
        Runs the full series of unit tests on auth.
        '''
        info('Running tests on the validate entry point.')

        connection = self.create_connection()

        tests = [
            self.test_urls,
            self.test_headers,
            self.test_body,
            self.test_model,
            self.test_success,
        ]

        try:
            # Get a session key to validate with.
            self.session_key = self.get_session_key(connection)

            for test in tests:
                test(connection)

        except socket.error:
            error('Could not connect to server. Check your config.')

        connection.close()

    def get_session_key(self, connection):
        '''
        Queries the publisher's server and returns a session key for use in
        future queries.
        '''
        # Create an Auth object to create the request to the publisher.
        auth = Auth()
        auth.config = self.config

        schemas = AUTH_SCHEMAS
        url, status, headers, body = auth.request(connection, schemas=schemas)

        return body['sessionKey']

    def get_url(self, api='paywallproxy', version=None, format='json',
                product=None, user='valid user'):
        '''
        Creates a url using the values in the config file.
        '''
        entry = 'validate'
        return Subcommand.get_url(self, entry=entry, api=api, version=version,
                                  format=format, product=product, user=user)

    def get_headers(self, charset = 'utf-8'):
        '''
        Creates a set of testing headers.
        '''
        token = 'PolarPaywallProxySessionv1.0.0 session:%s' % self.session_key

        return {'Accept': 'application/json',
                'Accept-Charset': charset,
                'Authorization': token}

    def get_body(self, user = 'valid user'):
        '''
        This entry point supports no body.
        '''
        return ''

    def test_body(self, connection):
        '''
        Test responses to bad json encoded resquests.
        '''
        info('Testing with body.')
        body = 'test'
        self.test_error(connection, 400, 'InvalidFormat', body=body)

    def test_model(self, connection):
        '''
        Test responses to requests with valid formatting but invalid data.
        '''
        info('Testing invalid product.')
        url = self.get_url(product=self.random_id())
        self.test_error(connection, 404, 'InvalidProduct', url=url)

        # Check to see if an invalid user is provided.
        parameters = self.config.items('invalid user')
        if len(parameters) > 0:
            # If an invalid user is provided, we can test a situation where one
            # user tries to use another users's session id.
            info('Testing session key copy attack.')
            url = self.get_url(user='invalid user')
            body = self.get_body(user='invalid user')
            code = 'SessionExpired'
            self.test_error(connection, 401, code, url=url, body=body)

    def test_success(self, connection):
        '''
        Test a successful request/response.
        '''
        info('Testing a successful validation.')
        self.request(connection, schemas=VALIDATE_SCHEMAS)
