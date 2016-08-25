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
Retrieves shell facts.
"""

import objectpath


# all the following helpers will be moved in iosxr-base:


def _jsonpath(obj, path, dtype=dict):

    opath = '$.'
    path_nodes = path.split('/')
    opath += '.'.join(map(lambda ele: "'{}'".format(ele), path_nodes))
    return _extract(obj, opath, dtype=dtype)


def _extract(obj, path, dtype=dict):
    tree = objectpath.Tree(obj)
    res = tree.execute(path)
    if not isinstance(res, dtype):
        if dtype is list:
            res = [res]
    return res


def shellutil(device, facts):

    """
    In the `facts` dictionary will set the following keys:
        * facts['hostname']: device hostname
    """

    systime = device.rpc.get('Cisco-IOS-XR-shellutil-oper:system-time/uptime')
    uptime = _jsonpath(systime, 'data/system-time/uptime')

    facts['hostname'] = _jsonpath(uptime, 'host-name')

    ipdomain = device.rpc.get('Cisco-IOS-XR-ip-domain-oper:ip-domain')

    facts['domain'] = _jsonpath(ipdomain, 'data/ip-domain/vrfs/vrf/server/domain-name')

    facts['fqdn'] = '{host}.{domain}'.format(
        host=facts['hostname'],
        domain=facts['domain']
    )
