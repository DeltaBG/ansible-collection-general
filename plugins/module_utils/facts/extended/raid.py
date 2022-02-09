# Collect facts related to RAID
#
# This file is part of Ansible Extended Facts
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re

from ansible.module_utils.facts.collector import BaseFactCollector
from ansible.module_utils.facts.utils import get_file_content, get_file_lines

class RaidFactCollector(BaseFactCollector):
    name = 'raid'
    _fact_ids = set()

    def collect(self, module=None, collected_facts=None):
        facts_dict = {}
        raid_facts = {} # This is default

        # Find SCSI devices
        if os.path.exists('/proc/scsi/scsi'):
            raid_facts['scsi_devices'] = []
            scsi_content = get_file_content('/proc/scsi/scsi')
            scsi_regex = re.compile(r'[H-h]ost:\s+(.*?)\s+.*[C-c]hannel:\s+(.*?)\s+[I-i]d:\s+(.*?)\s+[L-l]un:\s+(.*?)\n\s+[V-v]endor:\s+(.*?)\s+[M-m]odel:\s+(.*?)\s+[R-r]ev:\s+(.*?)\n\s+[T-t]ype:\s+(.*?)\s+.*')
            for controller in scsi_regex.findall(scsi_content):
                raid_facts['scsi_devices'].append({
                    'host'    : controller[0],
                    'channel' : controller[1],
                    'id'      : controller[2],
                    'lun'     : controller[3],
                    'vendor'  : controller[4],
                    'model'   : controller[5],
                    'rev'     : controller[6],
                    'type'    : controller[7]
                })

        # Find loaded kernel modules for RAID controllers
        if os.path.exists('/proc/modules'):
            raid_facts['modules'] = []
            modules_regex = re.compile(r'^(raid.*?|md|megaraid.*?|3w-[x9]xxx|aacraid|arcmsr|cciss|DAC960|dpt_i2o|gdth|hpsa|ips|mpt2?sas|mptscsih)\s+')
            for line in get_file_lines('/proc/modules'):
                m = modules_regex.search(line)
                if m:
                    raid_facts['modules'].append(m.groups()[0])

        facts_dict['raid'] = raid_facts
        return facts_dict
