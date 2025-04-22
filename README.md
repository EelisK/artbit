# artbit 🎨

> etymology: art made with heartbeats

## Dependencies

- [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [python](https://www.python.org/downloads/)
- [golang](https://go.dev/doc/install)
- [arp-scan](https://www.kali.org/tools/arp-scan/)

## Development

### Producer

Producer is used for generating heartbeats from a defined sensor.
Currently, we only support the MCP3008 ADC.

The producer send the hearbeats to a defined output.
See [./producer/internal/plugin/](plugins) for more details.

### Consumer

Consumer is used for consuming heartbeats from a defined input.
The heartbeats are then played from the speakers.

## Setup

```bash
ansible-playbook playbooks/setup.yml # Install dependencies and setup the environment
```
