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

from polar.paywall.test.schemas import ERROR_SCHEMAS

from httplib import HTTPSConnection, HTTPConnection

from logging import (basicConfig, DEBUG, INFO, WARNING, ERROR, CRITICAL,
    info, warning, error)

from ConfigParser import ConfigParser

from jsonschema import validate

# Used to generate random strings for testing.
from uuid import uuid4

# Used to decode and encode post bodies that contain json encoded data.
# Note that in python 2.5 and 2.6 the json module is called simplejson.
# In Python 2.7 and onwards, json is used.
try:
    from json import loads, dumps
except ImportError:
    from simplejson import loads, dumps

from random import randint


class Subcommand(object):
    '''
    Adds common functionality to subcommands.
    '''
    def set_log_level(self, log_level):
        '''
        Sets the log level. If None, the log_level will be warning.
        '''
        if log_level:
            levels = {}
            levels['debug'] = DEBUG
            levels['info'] = INFO
            levels['warning'] = WARNING
            levels['error'] = ERROR
            levels['critical'] = CRITICAL

            level = levels[log_level.lower()]
            basicConfig(level=level)

    def parse_config(self, config):
        '''
        Parses the configuration file.
        '''
        result = ConfigParser()
        result.readfp(config)
        return result

    def __call__(self, arguments):
        '''
        Called by the main file's callback mechanism. This function sets up
        the subcommand with logging and configuration and then calls the run
        function.
        '''
        # Setup logging and configuration.
        self.set_log_level(arguments.logLevel)
        self.config = self.parse_config(arguments.configuration)

        # Run the command.
        self.run(arguments)

    def run(self, arguments):
        '''
        Run the subcommand given the arguments. Inherit and override this
        this function to implement a subcommand.
        '''
        pass

    def create_connection(self):
        '''
        Creates a connection object using the parameters specified in the
        config file.
        '''
        protocols = {'http': HTTPConnection, 'https': HTTPSConnection}
        protocol = protocols[self.config.get('server', 'protocol')]

        return protocol(self.config.get('server', 'address'))

    def get_url(self, entry, api='paywallproxy', version=None, format='json',
                product=None, user='valid user'):
        '''
        Creates a url using the values in the config file.
        '''
        if not product:
            product = self.config.get('products', user)

        if not version:
            version = self.config.get('server', 'version')

        # format wasn't used to keep compatability with Python 2.5.
        params = (api, version, format, entry, product)
        return '/%s/%s/%s/%s/%s' % params

    def check_response(self, body, schemas=ERROR_SCHEMAS):
        '''
        Tests an error response body to see if it conforms to the proper error
        schema.
        '''
        version = self.config.get('server', 'version')
        schema = schemas[version]

        try:
            validate(body, schema)
        except ValueError, exception:
            warning('Response body does not match the schema: %s.' % \
                    str(exception))
            info(body)

    def check_headers(self, headers):
        '''
        Tests the headers to ensure that the content type is json.
        '''
        if 'Content-Type' not in headers:
            warning('The content type is not in the response.')
            return

        content_type = headers['Content-Type']
        if 'application/json' not in content_type:
            warning('The content type is not json: %s.' % content_type)

    def random_id(self):
        '''
        Generates a random unique id.
        '''
        return str(uuid4()).replace('-', '')

    def request(self, connection, url=None, headers=None, body=None,
                schemas=ERROR_SCHEMAS):
        '''
        Issue a request. If url, headers or body are None, then the default
        factory methods are used.
        '''
        if url is None:
            url = self.get_url()

        if headers is None:
            headers = self.get_headers()

        if body is None:
            body = self.get_body()

        # Encode the body using json. If a string is given, assume that it is
        # intended to be the body.
        if not isinstance(body, unicode) and not isinstance(body, str):
            body = dumps(body, ensure_ascii=False).encode('utf-8')

        # Unfortunately, without a body, python won't add a content length
        # header. It has to be manually added.
        if len(body) == 0:
            headers['Content-Length'] = 0

        # Make the request.
        connection.request('POST', url, body, headers)
        response = connection.getresponse()
        status = response.status

        # Check the headers.
        headers = response.msg
        self.check_headers(headers)

        # Check the body.
        try:
            body = loads(response.read())
        except ValueError, exception:
            error('Could not decode response: %s' % str(exception))

        self.check_response(body, schemas)

        return (url, status, headers, body)

    def test_error(self, connection, expected_status, expected_code,
                   url=None, headers=None, body=None, schemas=ERROR_SCHEMAS):
        '''
        Makes a request to check for an error.
        '''
        response = self.request(connection, url, headers, body, schemas)
        url, status, response_headers, response_body = response

        if status != expected_status:
            warning('The request to %s returned status %s and not %s' % \
                    (url, status, expected_status))
            info(response_body)

        code = response_body['error']['code']
        if code != expected_code:
            warning('The request to %s returned code %s and not %s' % \
                    (url, code, expected_code))
            info(response_body)

    def make_random_version(self):
        '''
        Creates a random version and tests to see if it is not the current
        version.
        '''
        server_version = self.config.get('server', 'version')
        version = server_version
        while version == server_version:
            major = randint(0, 9)
            minor = randint(0, 9)
            patch = randint(0, 9)
            version = 'v%i.%i.%i' % (major, minor, patch)
        return version

    def test_urls(self, connection):
        '''
        Tests the main url with bad url parameters.
        '''
        info('Testing an invalid api.')
        url = self.get_url(api='test')
        self.test_error(connection, 404, 'InvalidAPI', url=url)

        info('Testing an invalid version.')
        url = self.get_url(version=self.make_random_version())
        self.test_error(connection, 404, 'InvalidVersion', url=url)

        info('Testing an invalid format.')
        url = self.get_url(format='test')
        self.test_error(connection, 404, 'InvalidFormat', url=url)

    def test_headers(self, connection):
        '''
        Tests the servers response to invalid headers.
        '''
        info('Testing no auth header.')
        headers = self.get_headers()
        del headers['Authorization']
        self.test_error(connection, 400, 'InvalidAuthScheme', headers=headers)

        info('Testing no auth token.')
        headers = self.get_headers()
        headers['Authorization'] = ''
        self.test_error(connection, 400, 'InvalidAuthScheme', headers=headers)

        info('Testing invalid auth token.')
        headers = self.get_headers()
        headers['Authorization'] = self.random_id()
        self.test_error(connection, 400, 'InvalidAuthScheme', headers=headers)
