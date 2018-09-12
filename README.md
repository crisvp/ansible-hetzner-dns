# Hetzner Reverse DNS
This project includes two small modules to create reverse DNS 
records for Hetzner virtual servers.

## Installation
Clone this repository and copy the modules from `library/` to
your Ansible project's `library` directory.

### library/hcloud\_rdns.py
This module creates reverse DNS records through the Hetzner
Cloud API[1].

#### Example usage

```yaml
    - name: Create reverse DNS record (Hetzner Cloud)
      hcloud_rdns:
        token: MySecretToken
        ip: 192.0.2.23
        ptr: mail.example.com
      delegate_to: localhost
```

Delegation is not strictly necessary, but it prevents the token 
from leaving the control system.

#### Known issues
This does not work for IPv6 addresses that do not already have a 
reverse DNS record. This may be a limitation in the API.

### library/hetzner\_rdns.py
This module creates reverse DNS records through the Hetzner
Robot Webservice[2].

#### Example usage

```yaml
    - name: Create reverse DNS record (Hetzner Robot)
      hetzner_rdns:
        user: MyRobotWebserviceUsername
        password: MySecretPassword
        ip: 192.0.2.23
        ptr: mail.example.com
      delegate_to: localhost
```

As with the hcloud\_rdns module, delegation is not required.

### Return values
On success, both modules return the full response from the API. 
See the documentation (Cloud[1], Robot[2]) for more information.

[1]: https://docs.hetzner.cloud/
[2]: https://robot.your-server.de/doc/webservice/en.html
