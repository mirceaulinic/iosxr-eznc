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
Useful decorators.
"""


from __future__ import absolute_import

# import stdlib
from functools import wraps

# import third party
from lxml import etree
from ncclient.operations.rpc import RPCError as NCRPCError

# import local modules
from iosxr_eznc.exception import RPCError as XRRPCError


def raise_eznc_exception(fun):

    @wraps(fun)
    def _raise_eznc_exception(*vargs, **kvargs):
        try:
            return fun(*vargs, **kvargs)
        except NCRPCError as nc_err:
            print nc_err
            raise XRRPCError(vargs[0]._dev, nc_err)

    return _raise_eznc_exception


def qualify(param, oper=None):

    def _qualify_wrapper(fun):

        @wraps(fun)
        def _qualify(*vargs, **kvargs):
            if param in kvargs.keys():
                xml_req_tree = kvargs[param]
                if isinstance(xml_req_tree, basestring):
                    xml_req_tree = etree.fromstring(xml_req_tree)
                if xml_req_tree.get('xmlns') is None:
                    namespace = vargs[0]._dev._namespaces.get(xml_req_tree.tag, oper=oper)
                    if not namespace is None:
                        # cannot register with namespace
                        # probably the request will fail...
                        xml_req_tree.set('xmlns', namespace)
                        kvargs[param] = xml_req_tree
            return fun(*vargs, **kvargs)

        return _qualify

    return _qualify_wrapper
