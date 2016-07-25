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
from ncclient.operations.rpc import RPCError as NCRPCError

# import local modules
from iosxr_eznc.exception import RPCError as XRRPCError


def raise_eznc_exception(fun):

    @wraps(fun)
    def _raise_eznc_exception(*vargs, **kvargs):
        try:
            return function(*vargs, **kvargs)
        except NCRPCError as nc_err:
            raise XRRPCError(nc_err)

    return _raise_eznc_exception
