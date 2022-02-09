# Ansible Collection - deltabg.general

Delta Cloud Ltd. general collection

## Getting Started

This collection contains the following ressources.

- Module `deltabg.general.extended_facts` - return facts about RAID, IPMI and SMART

## Prerequisites

- [Ansible >= 2.9
- smartctl (smartmontools)
- ipmitool

## Installing

From Galaxy:
```sh
ansible-galaxy collection install deltabg.general
```

From GitHub:
```sh
ansible-galaxy collection install git+https://github.com/deltabg/ansible-collection-general.git,main
```

To install via the `requirements.yml` file:
```yaml
collections:
  - name: deltabg.general
```

or
```yaml
collections:
  - name: https://github.com/deltabg/ansible-collection-general.git
    type: git
    version: master
```
