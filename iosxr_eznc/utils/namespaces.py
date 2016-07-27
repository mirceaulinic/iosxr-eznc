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
Loads namespaces YAML file.
"""

from __future__ import absolute_import

# import stdlib
from os.path import splitext

# third party libs
import yaml

yaml_filename = splitext(__file__)[0] + '.yml'
with open(yaml_filename) as ns_file:
    MAP = yaml.load(ns_file)
