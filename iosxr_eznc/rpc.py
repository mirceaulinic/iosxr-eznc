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
NETCONF RPC classes.
"""

from __future__ import absolute_import

# import local modules
from iosxr_eznc.decorators import wrap_xml, qualify, raise_eznc_exception, jsonify


class _RPCBase(object):

    """
    Base RPC class.
    """

    def __init__(self, dev):
        self._dev = dev

    # not yet supported in ncclient 0.5.2
    # @raise_eznc_exception
    # def rpc(self, xml_rpc_command):
    #     return self._dev._conn.rpc(xml_rpc_command)

    # def __call__(self, xml_rpc_command):
    #     return self.rpc(xml_rpc_command)


class RPC(_RPCBase):

    """
    RPC calls.
    """

    def __init__(self, dev):
        _RPCBase.__init__(self, dev)

    @jsonify
    @raise_eznc_exception
    def get_schema(self, identifier, version=None, format=None):
        return self._dev._conn.get_schema(identifier,
                                          version=version,
                                          format=format)

    @jsonify
    @raise_eznc_exception
    @qualify('filter', True)
    @wrap_xml('filter')
    def _get(self, filter=None):
        return self._dev._conn.get(filter=filter)

    def get(self, filter):
        return self._get(filter=filter)

    @jsonify
    @raise_eznc_exception
    @qualify('filter', False)
    @wrap_xml('filter')
    def get_configuration(self, filter=None, source=None):
        if not source:
            source = 'running'
        return self._dev._conn.get_config(filter=filter, source=source)

    def get_config(self, filter=None, source=None):
        return self.get_configuration(filter=filter, source=source)

    @jsonify
    @raise_eznc_exception
    def lock(self, target='candidate'):
        return self._dev._conn.lock(target=target)

    @jsonify
    @raise_eznc_exception
    def unlock(self, target='candidate'):
        return self._dev._conn.unlock(target=target)

    @jsonify
    @raise_eznc_exception
    def edit_config(self,
                    config,
                    format='xml',
                    operation=None,
                    target='candidate',
                    test_option=None,
                    error_action=None):

        if not operation:
            operation = 'merge'

        if error_action:
            error_action = 'rollback-on-error'

        return self._dev._conn.edit_config(config,
                                           format=format,
                                           target=target,
                                           default_operation=operation,
                                           test_option=test_option,
                                           error_option=error_action)

    @jsonify
    @raise_eznc_exception
    def commit(self, confirmed=None, timeout=None):
        return self._dev._conn.commit(confirmed=confirmed,
                                      timeout=timeout)

    @jsonify
    @raise_eznc_exception
    def discard_changes(self):
        return self._dev._conn.discard_changes()

    @jsonify
    @raise_eznc_exception
    def validate(self, source='candidate'):
        return self._dev._conn.validate(source=source)

    @jsonify
    @raise_eznc_exception
    def delete_config(self, target):
        return self._dev._conn.delete_config(target)

    @jsonify
    @raise_eznc_exception
    def copy_config(self, source, target):
        return self._dev._conn.copy_config(source, target)
