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
Build device facts dictionary.
"""

# import stdlib
import sys
import inspect

# import local modules
# ~~~ exceptions ~~~
from iosxr_eznc.exception import FactsFetchError
# ~~~ facts fetchers ~~~
from iosxr_eznc.facts.shell import shellutil
from iosxr_eznc.facts.platform import platform


class Facts(dict):

    """
    Builds facts dictionary.
    """

    def __init__(self, dev, fetch=True):

        dict.__init__(self)

        self._dev = dev
        self._attach()
        if fetch:
            self.refresh()

    def _attach(self):

        """
        Attach facts fetchers to this object.
        """

        exclude = [
        ]  # in case will need to exclude anything

        self._fetchers = [
            fun_obj for (fun_name, fun_obj) in inspect.getmembers(sys.modules[__name__])
                if inspect.isfunction(fun_obj) and
                not fun_name.startswith('_') and
                fun_name not in exclude
        ]
        self._fetchers.reverse()

        __attach = lambda fun: self.__setattr__(fun.__name__, fun)

        map(__attach, self._fetchers)

        self._fetch_funs = map(lambda fun: fun.__name__, self._fetchers)


    def refresh(self, fun=None):

        """
        Refresh facts.

        :param fun: Specify the function that refreshes the facts.
        """

        _funs = self._fetchers

        if fun:
            _funs = [fetcher for fetcher in self._fetch_funs if fetcher == fun]
            if not _funs:
                raise FactsFetchError(
                    self._dev,
                    {
                        'fetcher': fun,
                        'msg': 'Invalid function name'
                    }
                )

        __collect = lambda fun: fun(self._dev, self)

        map(__collect, self._fetchers)
