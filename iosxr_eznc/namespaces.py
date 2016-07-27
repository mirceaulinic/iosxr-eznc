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
Handles IOS-XR namespaces.
"""

# import stdlib
import re
import six

# import third party
import yaml
import pyang
from pyang.translators.yin import emit_yin
from lxml import etree

# import local modules
from iosxr_eznc.exception import RPCError
from iosxr_eznc.utils import namespaces as NS


class _MetaString(str):

    def __init__(self, val=''):
        self._val = val

    def write(self, val):
        self._val += val

    def __str__(self):
        return self._val

    __repr__ = __str__


class _MetaPyangCtxOpts(object):

    yin_canonical = True
    yin_pretty_strings = True


class Namespaces(dict):

    _NS_REGEX = '^(.*)\/(.*)\/([a-zA-Z0-9-_]*)$'
    _CAPAB_REGEX = '^(.*)\/yang\/(.*)\?module=([a-zA-Z0-9-_]*)&(.*)$'
    # based on the capability format as per RFC 6020, paragraph 5.6.4

    def __init__(self, dev=None):

        self._dev = dev
        self._namespaces = {}
        if self._dev is not None:
            # load default namespaces as of IOS-XR 6.0.1
            self._load_default_namespaces()
            # device capabilities
            # some of them can be non-standard
            # i.e. the user can define custom YANG models
            self._capabilities = self._dev._conn.server_capabilities
            if self._dev._preload_schemas:
                # in case of custom modules
                # and if the pre-fetching is
                device_schemas = map(self._get_schema_capab, self._capabilities)
                default_schemas = map(self._get_schema_ns, self._namespaces.keys())
                custom_schemas = list(set(device_schemas) - set(default_schemas))
                self._fetch(custom_schemas)

    def _load_default_namespaces(self):

        """
        Loads the standard namespaces.
        """

        self._namespaces = NS.MAP

    def _get_schema_ns(self, ns):

        rgx_search = re.search(self._NS_REGEX, ns, re.I)
        if rgx_search and len(rgx_search.groups()) == 3:
            return rgx_search.groups()[2]
        return

    def _get_schema_capab(self, capability):

        rgx_search = re.search(self._CAPAB_REGEX, capability, re.I)
        if rgx_search and len(rgx_search.groups()) == 4:
            return rgx_search.groups()[2]
        return

    def init_pyang_context(self, repo_path=''):

        repo = pyang.FileRepository(repo_path, no_path_recurse=None)
        self.ctx = pyang.Context(repo)
        self.ctx.opts = _MetaPyangCtxOpts()

    @staticmethod
    def _get_container_name(ele):
        return ele.attrib.get('name', '')

    def yang_register(self, name, raw_yang_module):

        yin_output = _MetaString()
        yang_module = self.ctx.add_module(name, raw_yang_module)
        if yang_module.keyword != 'module':
            return
        emit_yin(self.ctx, yang_module, yin_output)
        # stripping namespaces
        yin_output = str(yin_output).replace('<xr:', '<')
        try:
            yin_tree = etree.fromstring(yin_output)
        except etree.XMLSyntaxError as err:
            return
        namespace = yin_tree.xpath('*[name()="namespace"]')[0].attrib.get('uri')
        # with these containers
        _containers = yin_tree.xpath('*[name()="container"] | *[name()="grouping"]/container')
        if not _containers:
            # no containers, no phun
            return
        containers = map(self._get_container_name, _containers)

        self.register({namespace: containers})

    def _reqister_dict(self, namespaces):

        for ns, containers in six.iteritems(namespaces):
            if isinstance(containers, list):
                self._namespaces[ns] = containers
            elif isinstance(containers, basestring):
                if ns not in self._namespaces.keys():
                    self._namespaces[ns] = []
                self._namespaces[ns].append(container)

    def register(self, namespaces):

        """
        Registers custom namespaces.
        The user is allowed to define its own capabilities and YANG models.
        Namespaces can be one of the following:

            * list: the user specifies a list of new schemas
            * dict, where:
                - the key means the name of the schema/namespace
                - the values represent the name of the containers associated with the schema
            * 1:1 dict, where:
                - the key is the name of the container
                - the value represents the namespace
        """

        if isinstance(namespaces, dict):
            return self._reqister_dict(namespaces)
        elif isinstance(namespaces, list):
            for namepsace in namespaces:
                if isinstance(namepsace, dict):
                    return self._reqister_dict(namepsace)

    def _fetch(self, schemas):

        """
        Retrieves the yang models from the device and builds a namespace-container map.
        """

        self.init_pyang_context()

        for schema in schemas:
            if schema is None:
                # could not parse properly the capability
                continue
            print 'retrieving schema', schema
            try:
                schema_content_reply = self._dev.op.get_schema(schema, format='yang')
            except RPCError:
                continue
            raw_yang_module = schema_content_reply.xpath('data')[0].text
            self.yang_register(schema, raw_yang_module)

    def get(self, container=None, oper=None):

        """
        Returns the namespace of a specific container.
        """
        if not container:
            return self._namespaces
        _nss = []
        for ns, containers in six.iteritems(self._namespaces):
            if oper is True and not ns.endswith('-oper'):
                continue
            if oper is False and not ns.endswith('-cfg'):
                continue
            for cont in containers:
                if cont.lower() == container.lower():
                    _nss.append(ns)
        if len(_nss) > 1:
            # ambiguous
            raise RPCError(self._dev, 'Please specify the namespace.')
        elif len(_nss) == 1:
            return _nss[0]
        return

    def __getitem__(self, containter):

        return self.get(container)
