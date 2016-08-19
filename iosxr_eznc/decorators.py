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
import json
import inspect
from functools import wraps

# import third party
import jxmlease
from lxml import etree
from ncclient.operations.retrieve import GetReply
from ncclient.operations.rpc import RPCError as NcRPCError
from ncclient.transport.errors import TransportError as NcTpError
from ncclient.operations.errors import TimeoutExpiredError as NcTEError

# import local modules
from iosxr_eznc.exception import RPCTimeoutError
from iosxr_eznc.exception import InvalidXMLReplyError
from iosxr_eznc.exception import ConnectionClosedError
from iosxr_eznc.exception import InvalidXMLRequestError
from iosxr_eznc.exception import RPCError as _XRRPCError


def _build_xml(xml_str):

    """
    Dynamically build an XML using reverse XPath.

    E.g.:
    >>> _build_xml('a/b/c')
    >>> '<a><b><c/></b></a>'
    """

    xml_tree = None
    # TODO: enhance this to allow also gRPC-type requests.
    xml_str_tags = xml_str.split('/')
    xml_tree = etree.Element(xml_str_tags[0])

    prev_subelem = xml_tree
    for subelem_tag in xml_str_tags[1:]:  # if any
        prev_subelem = etree.SubElement(prev_subelem, subelem_tag)

    return xml_tree


def _xml_obj_from_str(xml_str, dev):

    xml_req_tree = None

    try:
        xml_req_tree = etree.fromstring(xml_str)
    except etree.XMLSyntaxError:
        xml_req_tree = _build_xml(xml_str)

    if not etree.iselement(xml_req_tree):
        # still not XML obj, but should
        raise InvalidXMLRequestError(
            dev,
            err='Invalid request "{req}"'.format(
                req=xml_str
            )
        )

    return xml_req_tree


def raise_eznc_exception(fun):

    """
    Raises iosxr-eznc exception.
    Depending on the RPC method called, will try to raise the most appropriate exception.
    If unable to find a proper exception class, will raise the default RPCError.
    """

    def _get_rpc_error_class(exc):

        """
        Search for the exception class using the function name.
        """

        mod = __import__('iosxr_eznc.exception')
        for obj in inspect.getmembers(mod.exception):
            # digging into exceptions' module
            if obj[0] == exc and inspect.isclass(obj):
                # found ya
                return obj

    @wraps(fun)
    def _raise_eznc_exception(*vargs, **kvargs):
        # ~~~ vargs[0] is rpc obj ~~~
        _rpc_obj = vargs[0]
        _dev_obj = _rpc_obj._dev
        try:
            return fun(*vargs, **kvargs)
        except NcRPCError as nc_err:
            exc = '{}Error'.format(fun.__name__.title().replace('_', ''))
            XRRPCError = _get_rpc_error_class(exc)
            if not XRRPCError:
                # could not find the desired exception, throw the base
                XRRPCError = _XRRPCError
            err = nc_err.args[0]
            if not isinstance(err, dict):
                err = {
                    'err': nc_err.args[0]
                }
            err.update({
                'fun': 'rpc.{}'.format(fun.__name__),
                'args': vargs[1:] if len(vargs) > 0 else [],
                'kvargs': kvargs
            })
            raise XRRPCError(_dev_obj, err)
        except NcTEError as nc_err:
            err = {
                'fun': fun.__name__,
                'timeout': _dev_obj.timeout
            }
            raise RPCTimeoutError(_dev_obj, err)
        except NcTpError as nc_err:
            raise ConnectionClosedError(_dev_obj)

    return _raise_eznc_exception


def qualify(param, oper=None):

    """
    Apply the necessary namespace to the request.
    Request can be either:
        * valid XML
        * valid XPath-like selector (e.g.: container/tree/selector), respecting the structure tree of the YANG model
            e.g.:
            https://github.com/YangModels/yang/blob/master/vendor/cisco/xr/601/Cisco-IOS-XR-plat-chas-invmgr-oper.yang
            if the user needs only the `racks` data from the model above, can request using 'platform-inventory/racks'
    """

    def _qualify_wrapper(fun):

        @wraps(fun)
        def _qualify(*vargs, **kvargs):
            if param in kvargs.keys():
                xml_req_tree = kvargs[param]
                if isinstance(xml_req_tree, basestring):
                    xml_req_tree = _xml_obj_from_str(xml_req_tree, vargs[0]._dev)
                if xml_req_tree.get('xmlns') is None:
                    namespace = vargs[0]._dev._namespaces.get(xml_req_tree.tag, oper=oper)
                    if namespace is not None:
                        # cannot register with namespace
                        # probably the request will fail...
                        xml_req_tree.set('xmlns', namespace)
                        kvargs[param] = xml_req_tree

            return fun(*vargs, **kvargs)

        return _qualify

    return _qualify_wrapper


def wrap_xml(param, tag='filter'):

    """
    Wraps the filter XML specified in `param` into the `tag` if not already there.
    """

    def _wrap_xml_wrapper(fun):

        @wraps(fun)
        def _wrap_xml(*vargs, **kvargs):
            if param in kvargs.keys():
                xml_req_tree = kvargs[param]
                if isinstance(xml_req_tree, basestring):
                    xml_req_tree = _xml_obj_from_str(xml_req_tree, vargs[0]._dev)
                if xml_req_tree.tag != tag:
                    tag_elem = etree.Element(tag)
                    tag_elem.append(xml_req_tree)
                    kvargs[param] = tag_elem

            return fun(*vargs, **kvargs)

        return _wrap_xml

    return _wrap_xml_wrapper


def jsonify(fun):

    """
    Transforms the XML reply into a JSON.
    """

    def _jsonify(*vargs, **kvargs):
        ret = fun(*vargs, **kvargs)
        if isinstance(ret, GetReply):
            ret_xml = ret.data_xml
            ret_json = json.loads(json.dumps(jxmlease.parse(ret_xml)))
            return ret_json
        else:
            raise InvalidXMLReplyError(err='Cannot process reply from device')

    return _jsonify
