#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import netaddr
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: hetzner_rdns
short_description: Hetzner Cloud API reverse DNS
description:
     - Create or update a reverse DNS entry through Hetzner Robot API
version_added: "2.6"
options:
  token:
    description:
      - The API token for the project/context.
    required: true
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
  hcloud_rdns:
    token: sdf08sd08f09s80dfisudflajoas9df80w80e89r809283r
    ip: 195.123.456.789
    ptr: mailserver.example.com
'''

# ===========================================
# main


def main():

    module = AnsibleModule(
        argument_spec=dict(
            token=dict(required=True,),
            ip=dict(required=True),
            ptr=dict(required=True, aliases=['value', 'name'])
        ), supports_check_mode=True
    )

    token = module.params['token']
    ip = module.params['ip']
    ptr = module.params['ptr']

    update_server = None

    try:
        # We get all the servers because we don't know the name or id.
        url = 'https://api.hetzner.cloud/v1/servers'
        headers = {'Authorization': 'Bearer %s' % (token,)}

        # Verify current status
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise RuntimeError('Incorrect response from Hetzner WS: %s -> %d' %
                               (url, response.status_code))

        result = response.json()
        for server in result['servers']:
            ipv4_address = server['public_net']['ipv4']['ip']
            if ipv4_address == ip:
                dns_ptr = server['public_net']['ipv4'].get('dns_ptr', None)
                if dns_ptr is not None:
                    if dns_ptr == ptr:
                        module.exit_json(changed=False, msg="OK", value=response.json())
                    else:
                        update_server = server

            ipv6_network = netaddr.IPNetwork(server['public_net']['ipv6']['ip'])
            if ip in ipv6_network and 'dns_ptr' in server['public_net']['ipv6']:
                dns_ptr = server['public_net']['ipv6']['dns_ptr']
                for entry in dns_ptr:
                    if entry['ip'] == ip:
                        if entry['dns_ptr'] == ptr:
                            module.exit_json(changed=False, msg="OK", value=response.json())
                        else:
                            update_server = server

        if module.check_mode:
            module.exit_json(changed=True, msg="OK", value=response.json())

        if update_server is None:
            raise ValueError('could not find server with address %s' % (ip,))

        assert int(server['id']) > 0

        # Update record
        url = 'https://api.hetzner.cloud/v1/servers/{}/actions/change_dns_ptr'. \
              format(server['id'])

        response = requests.post(url, headers=headers, json={'ip': ip, 'dns_ptr': ptr})
        body = response.json()
        if response.status_code in (200, 201) and 'error' not in body:
            module.exit_json(changed=True, msg="OK", value=response.json())
        else:
            raise RuntimeError('Incorrect response from Hetzner WS: %s (%d): %s' %
                               (url, response.status_code, body))
    except Exception as e:
        module.fail_json(changed=False, msg='Failed in call to Hetzner WS: %s' % e.message)


main()
