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
Classes to manipulate connection with the IOS-XR device.
"""

from __future__ import absolute_import

# import stdlib
import os
import socket

# import third party libs
from ncclient import manager as netconf_ssh
from ncclient.transport.errors import AuthenticationError as NcAuthErr

# import local modules
import iosxr_eznc.exception
from iosxr_eznc.rpc import RPC
from iosxr_eznc.namespaces import Namespaces


class Device(object):

    ON_IOSXR = False

    def __init__(self, *vargs, **kvargs):

        """
        Init device object.
        """

        # hostname is mandatory
        # from IOS-XR 6.1 it is possible to have containers
        # the underlying system is CentOS
        # therefore platform / os checks are not enough
        # the user has to specify the hostname as 'localhost'
        # which makes the argument <hostname> mandatory
        hostname = vargs[0] if len(vargs) else (kvargs.get('host')
                                                or kvargs.get('hostname'))

        if not hostname:
            raise iosxr_eznc.exception.ConnectError('Please specify the hostname.')

        self._hostname = hostname
        self._port = kvargs.get('port', 830)
        self._preload_schemas = kvargs.get('preload_schemas', False)

        if hostname == 'localhost':
            # if the user specifies the host as 'localhost'
            # will assume is running in a container
            ON_IOSXR = True

        # continue processing params
        username = vargs[1] if len(vargs) > 1 else (kvargs.get('user')
                                                    or kvargs.get('username'))
        password = vargs[2] if len(vargs) > 2 else (kvargs.get('pass')
                                                    or kvargs.get('password')
                                                    or kvargs.get('passwd'))

        self._timeout = kvargs.get('timeout')

        if self.ON_IOSXR:
            # if on the device, can allow calling without specifying the user, etc.
            self._username = username or os.getenv('USER')  # takes the authenticated user
            self._password = None  # not necessary
            self._ssh_private_key_file = None
            self._ssh_config = None
        else:
            self._username = username
            self._password = password
            # ssh key options
            self._ssh_private_key_file = kvargs.get('ssh_private_key_file')
            self._ssh_config = kvargs.get('ssh_config')

        self._conn = None
        self.connected = False

    def open(self):

        allow_agent = self._password is None and self._ssh_private_key_file is None

        try:
            self._conn = netconf_ssh.connect(host=self._hostname,
                                             port=self._port,
                                             username=self._username,
                                             password=self._password,
                                             timeout=self._timeout,
                                             hostkey_verify=False,
                                             key_filename=self._ssh_private_key_file,
                                             allow_agent=allow_agent,
                                             ssh_config=self._ssh_config,
                                             device_params={'name': 'iosxr'})
        except NcAuthErr as auth_err:
            raise iosxr_eznc.exception.ConnectAuthError(dev=self)
        except socket.gaierror as host_err:
            raise iosxr_eznc.exception.ConnectError(dev=self, msg='Unknown host.')
        except Exception as err:
            raise iosxr_eznc.exception.ConnectError(dev=self, msg=err.message)  # original error

        # looking good
        self.connected = True
        self.rpc = RPC(self)
        self._namespaces = Namespaces(self)

        return self

    def close(self):

        self._conn.close_session()
        self.connected = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn.connected and not isinstance(exc_val, iosxr_eznc.exception.ConnectError):
            self.close()

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, val):
        self._hostname = val

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, val):
        self._username = val

    @property
    def password(self):
        return None

    @password.setter
    def password(self, val):
        self._password = val

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, val):
        self._timeout = val

    @property
    def namespaces(self):
        return self._namespaces

    @namespaces.setter
    def namespaces(self, vals):
        self._namespaces.register(vals)
