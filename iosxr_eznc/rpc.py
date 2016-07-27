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

# import third party modules
from lxml import etree

# import local modules
from iosxr_eznc.decorators import qualify, raise_eznc_exception


class Operational(object):

    """
    Executes operational RPC calls.
    """

    def __init__(self, dev):
        self._dev = dev

    @raise_eznc_exception
    def rpc(self, xml_rpc_command):
        return self._dev._conn.rpc(xml_rpc_command)

    @qualify('filter_xml', True)
    @raise_eznc_exception
    def _execute(self, filter_xml=None):

        # filter_xml is qualified after applying the decorator
        xml_rpc_command = etree.Element('get')
        filter_ele = etree.SubElement(xml_rpc_command, 'filter')
        if isinstance(filter_xml, basestring):
            filter_xml = etree.fromstring(filter_xml)
        filter_ele.append(filter_xml)

        return self.rpc(xml_rpc_command)

    def execute(self, filter_xml):
        return self._execute(filter_xml=filter_xml)

    @raise_eznc_exception
    def get_schema(self, identifier, version=None, format=None):
        return self._dev._conn.get_schema(identifier,
                                          version=version,
                                          format=format)

    @qualify('filter_xml', False)
    @raise_eznc_exception
    def get_configuration(self, source=None, filter_xml=None):
        return self._dev._conn.get_config(source=source,
                                          filter=filter_xml)

    def __call__(self, xml_rpc_command):
        return self.rpc(xml_rpc_command)


class Configuration(object):

    def __init__(self, dev):
        self._dev = dev

    @qualify('filter_xml', False)
    @raise_eznc_exception
    def get(self, filter_xml=None):
        return self._dev._conn.get(filter=filter_xml)

    @raise_eznc_exception
    def lock(self, target='candidate'):
        return self._dev._conn.lock(target=target)

    @raise_eznc_exception
    def unlock(self, target='candidate'):
        return self._dev._conn.unlock(target=target)

    @raise_eznc_exception
    def commit(self, confirmed=None, timeout=None):
        return self._dev._conn.commit(confirmed=confirmed,
                                      timeout=timeout)

    @raise_eznc_exception
    def discard_changes(self):
        return self._dev._conn.discard_changes()

    @raise_eznc_exception
    def validate(self, source='candidate'):
        return self._dev._conn.validate(source=source)

    @raise_eznc_exception
    def delete_config(self, target):
        return self._dev._conn.delete_config(target)

    @raise_eznc_exception
    def copy_config(self, source, target):
        return self._dev._conn.copy_config(source, target)
