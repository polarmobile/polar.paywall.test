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
    warning)

from ConfigParser import ConfigParser

from validictory import validate

# Used to generate random strings for testing.
from uuid import uuid4


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
        protocols = {'http':HTTPConnection, 'https': HTTPSConnection}
        protocol = protocols[self.config.get('server', 'protocol')]

        return protocol(self.config.get('server', 'address'))

    def check_response(self, body, schemas = ERROR_SCHEMAS):
        '''
        Tests an error response body to see if it conforms to the proper error
        schema.
        '''
        version = self.config.get('server', 'version')
        schema = schemas[version]

        try:
            validate(body, schema)
        except ValueError as exception:
            warning('Response body does not match the schema: %s.' % str(exception))

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
        return str(uuid4()).replace('-','')

    def request(self, connection, url=None, headers=None, body=None,
                schemas=ERROR_SCHEMAS):
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

        # Make the request.
        connection.request('POST', url, body, headers)
        response = connection.getresponse()
        status = response.status

        # Check the headers 
        headers = response.msg
        self.check_headers(headers)

        # Check the body.
        try:
            body = loads(response.read())
        except ValueError as exception:
            error('Could not decode response: %s' % str(exception))

        self.check_response(body, schemas)

        return (status, headers, body)

    def test_url(self, connection, url, expected_status, expected_code):
        '''
        Tests for processing of an invalid url.
        '''
        status, headers, body = self.request(connection, url=url)

        if status != expected_status:
            warning('The request to %s returned status %s and not %s' % \
                    (url, status, expected_status))

        if body['error']['code'] != expected_code:
            warning('The request to %s returned code %s and not %s' % \
                    (url, body['error']['code'], expected_code))

    def make_random_version(self):
        '''
        Creates a random version and tests to see if it is not the current
        version.
        '''
        server_version = self.config.get('server','version')
        version = server_version
        while version == server_version:
            version = 'v%i.%i.%i' % (randint(0,9), randint(0,9), randint(0,9))
        return version

    def test_urls(self, connection):
        '''
        Tests the main url with bad url parameters.
        '''
        info('Testing an invalid api.')
        url = self.get_url(api='test')
        self.test_url(connection, url, 404, 'InvalidAPI')

        info('Testing an invalid version.')
        url = self.get_url(version=self.make_random_version())
        self.test_url(connection, url, 404, 'InvalidVersion')

        info('Testing an invalid version.')
        url = self.get_url(version=self.make_random_version())
        self.test_url(connection, url, 404, 'InvalidVersion')

    def test_success(self, connection):
        '''
        Test a successful request/response.
        '''
        info('Testing a successful authentication.')
        self.request(connection, schemas=AUTH_SCHEMAS)
