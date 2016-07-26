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

from setuptools import setup, find_packages
from pip.req import parse_requirements
import uuid

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())

reqs = [str(ir.req) for ir in install_reqs]

__version__ = '2016.7.22'

setup(
    name = 'iosxr-eznc',
    version  = __version__,
    packages = find_packages(),
    platforms = 'any',
    install_requires = reqs,
    include_package_data = True,
    description = 'Python library for Cisco IOS-XR automation via NETCONF',
    author = 'Mircea Ulinic',
    author_email = 'mircea@cloudflare.com',
    url = 'https://github.com/mirceaulinic/iosxr-eznc',  # use the URL to the github repo
    download_url = 'https://github.com/mirceaulinic/iosxr-eznc/tarball/%s' % __version__,
    keywords = ['network', 'automation', 'NETCONF', 'IOS-XR', 'IOSXR', 'Cisco'],
    license = 'Apache 2.0',
    scripts = ['utils/iosxr_yang_namespaces'],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Markup :: XML',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
      ]
)
