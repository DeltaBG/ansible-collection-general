#!/usr/bin/python
#
# MIT License
#
# Copyright (c) 2022 Nedelin Petkov <mlg@abv.bg>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: deltabg.general.extended_facts
version_added: historical
short_description: Module for extended Ansible facts
description:
  - Collecting information about the system in favor
author:
  - Nedelin Petkov (https://github.com/mlg1/)
options:
    gather_subset:
        version_added: "2.10"
        description:
            - "If supplied, restrict the additional facts collected to the given subset.
              Possible values: C(all), C(raid), C(ipmi) and C(smartctl)"
        type: list
        elements: str
        default: "all"
    gather_timeout:
        version_added: "2.10"
        description:
            - Set the default timeout in seconds for individual fact gathering.
        type: int
        default: 10
    filter:
        version_added: "2.10"
        description:
            - If supplied, only return facts that match one of the shell-style
              (fnmatch) pattern. An empty list basically means 'no filter'.
              As of Ansible 2.11, the type has changed from string to list
              and the default has became an empty list. A simple string is
              still accepted and works as a single pattern. The behaviour
              prior to Ansible 2.11 remains.
        type: list
        elements: str
        default: []
    fact_path:
        version_added: "2.10"
        description:
            - Path used for local ansible facts (C(*.fact)) - files in this dir
              will be run (if executable) and their results be added to C(ansible_local) facts.
              If a file is not executable it is read instead.
              File/results format can be JSON or INI-format. The default C(fact_path) can be
              specified in C(ansible.cfg) for when setup is automatically called as part of
              C(gather_facts).
              NOTE - For windows clients, the results will be added to a variable named after the
              local file (without extension suffix), rather than C(ansible_local).
            - Since Ansible 2.1, Windows hosts can use C(fact_path). Make sure that this path
              exists on the target host. Files in this path MUST be PowerShell scripts C(.ps1)
              which outputs an object. This object will be formatted by Ansible as json so the
              script should be outputting a raw hashtable, array, or other primitive object.
        type: path
        default: /etc/ansible/facts.d
'''

EXAMPLES = r'''
# Display facts from all hosts
# ansible all -m deltabg.general.extended_facts

# Restrict additional gathered facts to ipmi
# ansible all -m deltabg.general.extended_facts -a 'gather_subset=ipmi'

- name: Gathering all extended facts
  deltabg.general.extended_facts:

- name: Gathering all extended facts - alternative
  deltabg.general.extended_facts:
    gather_subset:
      - all

- name: Gathering extended facts only for raid
  deltabg.general.extended_facts:
    gather_subset:
      - raid
'''

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils._text import to_text
from ansible.module_utils.facts import ansible_collector
from ansible.module_utils.facts.collector import CollectorNotFoundError, CycleFoundInFactDeps, UnresolvedFactDep
from ansible.module_utils.facts.namespace import PrefixFactNamespace

from ansible_collections.deltabg.general.plugins.module_utils.facts.extended.raid import RaidFactCollector
from ansible_collections.deltabg.general.plugins.module_utils.facts.extended.ipmi import IpmiFactCollector
from ansible_collections.deltabg.general.plugins.module_utils.facts.extended.smartctl import SmartctlFactCollector

def main():
    module = AnsibleModule(
        argument_spec=dict(
            gather_subset=dict(default=["all"], required=False, type='list', elements='str'),
            gather_timeout=dict(default=10, required=False, type='int'),
            filter=dict(default=[], required=False, type='list', elements='str'),
            fact_path=dict(default='/etc/ansible/facts.d', required=False, type='path'),
        ),
        supports_check_mode=True,
    )

    gather_subset = module.params['gather_subset']
    gather_timeout = module.params['gather_timeout']
    filter_spec = module.params['filter']

    minimal_gather_subset = frozenset()

    all_collector_classes = [
        RaidFactCollector,
        IpmiFactCollector,
        SmartctlFactCollector
    ]

    # rename namespace_name to root_key?
    namespace = PrefixFactNamespace(namespace_name='ansible',
                                    prefix='ansible_')

    try:
        fact_collector = ansible_collector.get_ansible_collector(all_collector_classes=all_collector_classes,
                                                                 namespace=namespace,
                                                                 filter_spec=filter_spec,
                                                                 gather_subset=gather_subset,
                                                                 gather_timeout=gather_timeout,
                                                                 minimal_gather_subset=minimal_gather_subset)
    except (TypeError, CollectorNotFoundError, CycleFoundInFactDeps, UnresolvedFactDep) as e:
        # bad subset given, collector, idk, deps declared but not found
        module.fail_json(msg=to_text(e))

    facts_dict = fact_collector.collect(module=module)

    module.exit_json(ansible_facts=facts_dict)


if __name__ == '__main__':
    main()
