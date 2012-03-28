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

# Used to parse command line arguments and dispatch to the appropriate
# subcommands.
from argparse import ArgumentParser, FileType

# Subcommands.
from temlate import template


def main():
    '''
    Main entry point for the utility. It parses sys.argv and calls the
    selected function.
    '''
    parser = get_parser()
    arguments = parser.parse_args()
    arguments.callback(arguments)


def get_parser():
    '''
    Create the top level parser.
    '''
    # Create the main parser.
    description = ('Paywall deployment tool used to test to see if a proxy '
                   'conforms to a given api.')
    parser = ArgumentParser(description=description)
    subparsers = parser.add_subparsers()

    # Create the subcommands. Subcommands are mapped to different entry
    # points in the system.
    create_auth_parser(subparsers)


def create_configuration_argument(subparser):
    '''
    A helper function used to import the configuration file.
    '''
    help = ('Path to the configuration file. Use the template command to'
            'generate a sample configuration.')
    subparser.add_argument('configuration', help=help, type=FileType('r'))


def create_log_level_argument(subparser):
    '''
    Lets the user specify the log level used when running the application.
    '''
    help = ('Set the log level.')
    choices = ('debug', 'info', 'warning', 'error', 'critical')
    subparser.add_argument('-l', '--logLevel', help=help, required=False,
                           choices=choices)


def create_subparser(subparsers, name, help, callback):
    '''
    Many of the subcommands in this system follow the same structure.
    '''
    subparser = subparsers.add_parser(name, help=help)

    create_configuration_argument(subparser)
    create_log_level_argument(subparser)

    # Register a callback that will be called if this subparser is selected.
    subparser.set_defaults(callback=callback)


def create_template(subparsers):
    '''
    A subparser for the "auth" entry point in the paywall proxy.
    '''
    help = ('Prints a sample configuration file. Pipe the results of this '
            'file to save it.')
    subparser = subparsers.add_parser(name, help=help)

    # Register a callback that will be called if this subparser is selected.
    subparser.set_defaults(callback=template)


def create_auth_parser(subparsers):
    '''
    A subparser for the "auth" entry point in the paywall proxy.
    '''
    pass


def create_validate_parser(subparsers):
    '''
    A subparser for the "validate" entry point in the paywall proxy.
    '''
    pass


# If the script is called directly, call the main application.
if __name__ == '__main__':
    main()
