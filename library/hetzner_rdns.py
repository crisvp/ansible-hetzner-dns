#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from requests.compat import urljoin, quote_plus
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: hetzner_rdns
short_description: Hetzner Robot API reverse DNS
description:
     - Create or update a reverse DNS entry through Hetzner Robot API
version_added: "2.6"
options:
  user:
    description:
      - The username for the Hetzner Robot API
    required: true
    aliases: [ 'username' ]
  password:
    description:
      - The password for the Hetzner Robot API
    required: true
    aliases: [ 'pass' ]
  ip:
    description:
      - <
        The IPv4 or 6 address the PTR record should point to.
        This takes an address in forward notation (e.g. 127.0.0.1),
        not in regular reverse notation (e.g. 1.0.0.127.in-addr.arpa).
    required: true
  ptr:
    description:
      - The value for the PTR record (FQDN, e.g. myhost.example.com)
    required: true
    aliases: [ 'value', 'name' ]
author: Cris van Pelt
'''

EXAMPLES = '''
- name: Set a reverse DNS record for 195.123.456.789
  hetzner_rdns:
    user: d9f834d'fg
    password: @#$fjKD909djf
    ip: 195.123.456.789
    ptr: mailserver.example.com
'''

# ===========================================
# main


def main():

    module = AnsibleModule(
        argument_spec=dict(
            user=dict(required=True, aliases=['username']),
            password=dict(required=True),
            ip=dict(required=True),
            ptr=dict(required=True, aliases=['value', 'name'])
        ), supports_check_mode=True
    )

    user = module.params['user']
    password = module.params['password']
    ip = module.params['ip']
    ptr = module.params['ptr']

    try:
        url = urljoin('https://robot-ws.your-server.de/rdns/',
                      quote_plus(ip))

        # Verify current status
        response = requests.get(url, auth=(user, password))
        if response.status_code == 200:
            result = response.json()
            if result['ip'] == 'ip' and result['ptr'] == ptr:
                module.exit_json(changed=False, msg="OK", value=response.json())

            if module.check_mode:
                module.exit_json(changed=True, msg="OK", value=response.json())
        else:
            raise RuntimeError('Incorrect response from Hetzner WS: %s -> %d' %
                               (url, response.status_code))

        # Update record
        response = requests.post(url, json={'rdns': {'ip': ip, 'ptr': ptr}},
                                 auth=(user, password))
        if response.status_code in (200, 201):
            module.exit_json(changed=True, msg="OK", value=response.json())
        else:
            raise RuntimeError('Incorrect response from Hetzner WS: %s -> %d' %
                               (url, response.status_code))
    except Exception as e:
        module.fail_json(changed=False, msg='Failed in call to Hetzner WS: %s' % e.message)


main()
