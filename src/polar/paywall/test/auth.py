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


from polar.paywall.test.subcommand import Subcommand

from logging import info, warning

from json import loads, dumps

import socket


class Auth(Subcommand):
    '''
    Called by the auth subcommand in main.
    '''
    def run(self, arguments):
        '''
        Runs the full series of unit tests on auth.
        '''
        info('Running tests on the auth entry point.')

        connection = self.create_connection()

        #print self.get_url()
        #print self.get_headers()
        #print self.get_body()
        try:
            print self.request(connection)

        except socket.error:
            warning('Could not connect to server. Check your config.')

        connection.close()

    def get_url(self, api='paywallproxy', version=None, format='json',
                product=None, user='valid user'):
        '''
        Creates a url using the values in the config file.
        '''
        if not product:
            product = self.config.get('products', user)

        if not version:
            version = self.config.get('server', 'version')

        parameters = {'api': api, 'version': version, 'format': format,
                      'product': product}
        return '/{api}/{version}/{format}/auth/{product}'.format(**parameters)

    def get_headers(self, charset = 'utf-8'):
        '''
        Creates a set of testing headers.
        '''
        return {'Accept': 'application/json',
                'Accept-Charset': charset,
                'Authorization': 'PolarPaywallProxyAuthv1.0.0'}

    def get_body(self, user = 'valid user'):
        '''
        Get a sample body for auth testing. Possible choices for user are
        'valid user' and 'invalid user'.
        '''
        result = {
            'device': {
                'os_version': 'test',
                'model': 'test',
                'manufacturer': 'test',
            },
            'authParams': {},
        }

        # Extract authentication parameters from the configuration file.
        for option in self.config.options(user):
            result['authParams'][option] = self.config.get(user, option)

        return result

    def request(self, connection, url=None, headers=None, body=None):
        '''
        Issue a request. If url, headers or body are None, then the default
        factory methods are used.
        '''
        if not url:
            url = self.get_url()

        if not headers:
            headers = self.get_headers()

        if not body:
            body = dumps(self.get_body())

        connection.request('POST', url, body, headers)
        response = connection.getresponse()

        status = response.status
        headers = response.msg
        body = response.read()

        return (status, headers, body)
