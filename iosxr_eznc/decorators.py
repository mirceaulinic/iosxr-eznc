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
import inspect
from functools import wraps

# import third party
from lxml import etree
from ncclient.transport.errors import TransportError as NcTpError
from ncclient.operations.errors import TimeoutExpiredError as NcTEError
from ncclient.operations.rpc import RPCError as NcRPCError

# import local modules
from iosxr_eznc.exception import RPCError as _XRRPCError
from iosxr_eznc.exception import ConnectionClosedError
from iosxr_eznc.exception import RPCTimeoutError


def raise_eznc_exception(exc, msg=None):

    def _get_rpc_error_class(exc):

        mod = __import__('iosxr_eznc.exception')
        for obj in inspect.getmembers(mod.exception):
            if obj[0] == exc and inspect.isclass(obj):
                return obj

    def _raise_eznc_exception_wrapper(fun):

        @wraps(fun)
        def _raise_eznc_exception(*vargs, **kvargs):
            try:
                return fun(*vargs, **kvargs)
            except NcRPCError as nc_err:
                XRRPCError = _get_rpc_error_class(exc)
                if not XRRPCError:
                    XRRPCError = _XRRPCError
                if msg:
                    nc_err.args[0]['msg'] = msg
                raise XRRPCError(vargs[0]._dev, nc_err.args[0])
            except NcTpError as nc_err:
                nc_err.args[0]['timeout'] = vargs[0]._dev.timeout
                raise RPCTimeoutError(vargs[0]._dev, nc_err.args[0])
            except NcTEError as nc_err:
                raise ConnectionClosedError(vargs[0]._dev)

        return _raise_eznc_exception

    return _raise_eznc_exception_wrapper


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
