[![PyPI](https://img.shields.io/pypi/v/iosxr-eznc.svg)](https://pypi.python.org/pypi/iosxr-eznc)
[![PyPI](https://img.shields.io/pypi/dm/iosxr-eznc.svg)](https://pypi.python.org/pypi/iosxr-eznc)

## ABOUT

iosxr-eznc is a Python library to manage Cisco devices running IOS-XR using NETCONF and YANG models as per [RFC 6020](https://tools.ietf.org/html/rfc6020).

## INSTALLATION

YANG models are supported exclusively through version 1.1 of NETCONF, therefore at least version 0.5.2 of ncclient is required.

#### Requirements:

* version >= Python 2.6 or Python3
* ncclient 0.5.2+
* pyang


### Install via pip:

````bash
pip install ncclient
````

## USGAE

Firstly make sure that netconf-yang is enabled on the device:

    # netconf-yang agent ssh

#### Connect to the device:

````python
from pprint import pprint
from iosxr_eznc import Device

dev = Device(host='edge01.bjm01', user='netconf', password='!Love105-XR')
dev.open()
pprint(dev.facts)
dev.close()
````

## LICENSE

Copyright 2016 CloudFlare, Inc.

Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
