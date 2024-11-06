# artbit 🎨

> etymology: art made with heartbeats

## Dependencies

- [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [python](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [poetry](https://python-poetry.org/docs/#installation)
- [arp-scan](https://www.kali.org/tools/arp-scan/)

## Development

```bash
ansible-playbook playbooks/setup.yml # Install dependencies and setup the environment on raspberry PIs on the network
ansible-playbook playbooks/fetch.yml # Fetch data from raspberry PIs on the network
python -m artbit # Run the application
```
