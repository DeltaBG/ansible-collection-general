# Collect facts related to smartctl
#
# This file is part of Ansible Extended Facts
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible.module_utils.facts.collector import BaseFactCollector
from ansible.module_utils.facts.utils import get_file_content, get_file_lines

class SmartctlFactCollector(BaseFactCollector):
    name = 'smartctl'
    _fact_ids = set()

    def collect(self, module=None, collected_facts=None):
        facts_dict = {}
        smartctl_facts = [] # This is default

        smartctl_bin = module.get_bin_path('smartctl')
        if smartctl_bin:
            rc, smartctl_output, err = module.run_command([smartctl_bin, '--scan-open'])
            smartctl_regex = re.compile(r'^(/.*?)\s+-d\s+(.*?)\s+#\s+.*', re.MULTILINE)
            for device in smartctl_regex.findall(smartctl_output):
                smartctl_facts.append({
                    'device'         : device[0],
                    'type'           : device[1]
                })

        facts_dict[self.name] = smartctl_facts
        return facts_dict
