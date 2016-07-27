# -*- coding: utf-8 -*-
# Copyright 2016 CloudFlare, Inc. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Defines custom Exception classes that the library might raise.
"""

from __future__ import absolute_import

# import stdlib
import six


class ConnectError(Exception):
    def __init__(self, dev=None, msg=None):
        self._dev = dev
        self._msg = msg
    def __repr__(self):
        if self._dev:
            if self._msg:
                return '{cls} (host: {host}, message: {msg})'.format(
                    self.__class__.__name__,
                    host=self._dev.hostname,
                    msg=self._msg
                )
            else:
                return '{cls} (host: {host})'.format(
                    self.__class__.__name__,
                    host=self._dev.hostname
                )
        else:
            return self._msg
    __str__ = __repr__


class RPCError(Exception):

    def __init__(self, dev, err):
        self._dev = dev
        self._err = err

    def __repr__(self):
        _err_parts = []
        if self._err:
            for detail, value in six.iteritems(self._err.args[0]):
                if detail == 'info':
                    continue
                if value:
                    _err_parts.append('{detail}: {value}'.format(
                            detail=detail,
                            value=value
                        )
                    )

        return '{dev} ({errors})'.format(
            dev=self._dev.hostname,
            errors=', '.join(_err_parts)
        )

    __str__ = __repr__


class ConnectAuthError(ConnectError):

    pass


class ConnectUnknownHostError(ConnectError):

    pass


class ConnectionClosedError(ConnectError):

    def __init__(self, dev):
        ConnectError.__init__(self, dev=dev, msg='Connection closed.')
        dev.connected = False


class TimeoutExpiredError(RPCError):

    pass


class LockError(RPCError):

    pass


class UnlockError(RPCError):

    pass


class RPCTimeoutError(RPCError):

    pass


class CommitError(RPCError):

    pass


class DiscardChangesError(RPCError):

    pass


class DeleteConfigError(RPCError):

    pass


class ValidateError(RPCError):

    pass


class CopyConfigError(RPCError):

    pass


class RollbackError(RPCError):

    pass
