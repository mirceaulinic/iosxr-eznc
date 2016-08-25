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

import time
import objectpath

from iosxr_eznc.facts.personality import personality


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


def platform(device, facts):

    """
    In the `facts` dictionary will set the following keys:
        * facts['model']: device model
        * facts['serial']: serial number
        * facts['slots']: list of slots
        * facts['uptime']: uptime in seconds
        * facts['version']: OS version
    """

    platform_json = device.rpc.get('Cisco-IOS-XR-plat-chas-invmgr-oper:platform-inventory')
    rack_tree = _jsonpath(platform_json, 'data/platform-inventory/racks/rack')
    chassis_attributes = _jsonpath(rack_tree, 'attributes/basic-info')

    facts['model'] = _jsonpath(chassis_attributes, 'model-name')
    facts['serial'] = _jsonpath(chassis_attributes, 'serial-number')
    facts['os_version'] = _jsonpath(chassis_attributes, 'software-revision')
    facts['description'] = _jsonpath(chassis_attributes, 'description')

    personality(device, facts)

    slot_tree = _jsonpath(rack_tree, 'slots/slot', list)

    main_slot = '0'
    if facts['personality'] == 'XRv':
        main_slot = '16'

    facts['slots'] = [
        slot.get('name') for slot in slot_tree if slot.get('name') != main_slot
    ]

    uptime_generator = list(
        _extract(
            slot_tree,
            "$.*[@.name is '{main_slot}'].cards.card.attributes.'fru-info'.'module-up-time'.'time-in-seconds'".format(
                main_slot=main_slot
            )
        )
    )

    if uptime_generator:
        facts['uptime'] = time.time() - float(uptime_generator[0])
    else:
        facts['uptime'] = 0.0
