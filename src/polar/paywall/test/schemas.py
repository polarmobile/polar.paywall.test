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

V1_0_0_AUTH_SCHEMA = {
    "type": "object",
    "required": True,
    "properties": {
        "sessionKey": {
            "type": "string",
            "required": True,
        },
        "products": {
            "type": "array",
            "required": True,
            "items": {
                "type": "string"
            }
        }
    }
}

# The response from the validate and authenticate commands are the same.
V1_0_0_VALIDATE_SCHEMA = V1_0_0_AUTH_SCHEMA

V1_0_0_ERROR_SCHEMA = {
    "type": "object",
    "required": True,
    "properties": {
        "error": {
            "type": "object",
            "required": True,
            "properties": {
                "code": {
                    "type": "string",
                    "required": True,
                },
                "message": {
                    "type": "string",
                    "required": True,
                },
                "resource": {
                    "type": "string",
                    "required": True,
                }
            }
        },
        "debug": {
            "type": "object",
            "required": False,
            "properties": {
                "message": {
                    "type": "string",
                    "required": True,
                }
            }
        }
    }
}

# A global set of dictionary of json schemas.
AUTH_SCHEMAS = {
    'v1.0.0': V1_0_0_AUTH_SCHEMA,
}

VALIDATE_SCHEMAS = {
    'v1.0.0': V1_0_0_VALIDATE_SCHEMA,
}

ERROR_SCHEMAS = {
    'v1.0.0': V1_0_0_ERROR_SCHEMA,
}

