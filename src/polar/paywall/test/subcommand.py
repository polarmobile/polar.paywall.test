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

    def status_warning(self, test, status):
        '''
        A helper function for reporting a bad status warning.
        '''
        warning('Wrong status received when testing %s: %s.' % (test, status))

    def code_warning(self, test, code):
        '''
        A helper function to print a bad error code warning.
        '''
        warning('Wrong error code received when testing %s: %s.' % \
                (test, status))
