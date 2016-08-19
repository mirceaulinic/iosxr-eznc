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
Retrieves platform specific facts.
"""

import objectpath


def _dict_to_list(obj):

    return [obj]


def _jsonpath(path):

    opath = '$.'
    path_nodes = path.split('/')
    opath += '.'.join(map(lambda ele: "'{}'".format(ele), path_nodes))
    return opath


def _extract(obj, path, dtype=dict):

    tree = objectpath.Tree(obj)
    opath = _jsonpath(path)
    res = tree.execute(opath)

    if not isinstance(res, dtype):
        if dtype is list:
            res = [res]

    return res


def platform_facts(device, facts):

    """
    In the `facts` dictionary will set the following keys:
        * facts['model']: device model
        * facts['serial']: serial number
        * facts['racks']: list of racks
    """

    platform_json = device.rpc.get('platform-inventory')  # retrieve platform-inventory
    rack_tree = _extract(platform_json, 'data/platform-inventory/racks/rack')
    chassis_attributes = _extract(rack_tree, 'attributes/basic-info')

    facts['model'] = _extract(chassis_attributes, 'model-name')
    facts['serial'] = _extract(chassis_attributes, 'serial-number')
