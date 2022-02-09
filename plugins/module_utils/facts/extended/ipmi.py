# Collect facts related to IPMI
#
# This file is part of Ansible Extended Facts
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re

from ansible.module_utils.facts.collector import BaseFactCollector
from ansible.module_utils.facts.utils import get_file_content, get_file_lines

class IpmiFactCollector(BaseFactCollector):
    name = 'ipmi'
    _fact_ids = set()

    def collect(self, module=None, collected_facts=None):
        facts_dict = {}
        ipmi_facts = {} # This is default
        have_ipmi = False

        ipmitool_bin = module.get_bin_path('ipmitool')

        # Find loaded kernel modules for IPMI Adapter
        if os.path.exists('/proc/modules'):
            for line in get_file_lines('/proc/modules'):
                if re.search('^ipmi_.*', line):
                    have_ipmi = True

        if have_ipmi:
            if ipmitool_bin:
                rc, ipmitool_output, err = module.run_command([ipmitool_bin, 'lan', 'print', '1'])
                ipmitool_regex = re.compile(r'IP\sAddress\sSource\s+:\s(?P<source>[ a-zA-Z]+)|IP\sAddress\s+:\s(?P<address>[.0-9]+)|Subnet\sMask\s+:\s(?P<netmask>[.0-9]+)|MAC\sAddress\s+:\s(?P<macaddress>[:0-9a-fA-F]+)|SNMP\sCommunity\sString\s+:\s(?P<snmp_community>[ -.#@=:_a-zA-Z]+)|Default\sGateway\sIP\s+:\s(?P<gateway>[.0-9]+)|802\.1q\sVLAN\sID\s+:\s(?P<vlan_id>[0-9]+)')
                for line in ipmitool_output.split('\n'):
                    m = ipmitool_regex.search(line)
                    if m:
                        for key, value in m.groupdict().items():
                            if value:
                                ipmi_facts[key] = value

        facts_dict[self.name] = ipmi_facts
        return facts_dict
