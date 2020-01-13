__author__ = 'camrossi'


#!/usr/bin/env python
#
# Written by Toru Okatsu @ Cisco Systems, August 20th 2014
#
# Modified by Camillo Rossi @ Cisco Systems, February 2015
#

import argparse
import re
import cobra.mit.access
import cobra.mit.session
from prettytable import PrettyTable
import warnings
import yaml

warnings.filterwarnings("ignore")
vlan_list_f1 = set()
vlan_list_f2 = set()

all_vlans = set()

for i in range(1,4097):
    all_vlans.add(i)



f = open('credentials_fab1.yaml', 'r')
credentials = yaml.load(f)
f.close()


ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'],
                                    secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print 'Logging in to ' + credentials['host']
md.login()

# Get node list
print 'Getting VLANs Pools'
q = cobra.mit.request.ClassQuery('fvnsEncapBlk')
q.subtree = 'full'
mos = md.query(q)
for mo in mos:
    #Need to use getattr since from is a reserved keyword
    start_str = getattr(mo,'from')
    stop_str = mo.to
    # print('START ' + start_str)
    if 'vlan-' in start_str and 'vlan-' in stop_str:
        start = int(start_str.strip('vlan-'))
        stop = int(stop_str.strip('vlan-'))
        for i in range(start, stop + 1):
            # print i
            vlan_list_f1.add(i)
    # print('STOP ' + stop_str)


f = open('credentials_fab2.yaml', 'r')
credentials = yaml.load(f)
f.close()


ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'],
                                    secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print 'Logging in to ' + credentials['host']
md.login()

# Get node list
print 'Getting VLANs Pools'
q = cobra.mit.request.ClassQuery('fvnsEncapBlk')
q.subtree = 'full'
mos = md.query(q)
for mo in mos:
    #Need to use getattr since from is a reserved keyword
    start_str = getattr(mo,'from')
    stop_str = mo.to
    # print('START ' + start_str)
    if 'vlan-' in start_str and 'vlan-' in stop_str:
        start = int(start_str.strip('vlan-'))
        stop = int(stop_str.strip('vlan-'))
        for i in range(start, stop + 1):
            vlan_list_f2.add(i)
    # print('STOP ' + stop_str)



print sorted(vlan_list_f1)
print sorted(vlan_list_f2)

if 960 not in vlan_list_f2 and 960 not in vlan_list_f1:
    print ' frrr'

print (all_vlans - vlan_list_f1)
print (all_vlans - vlan_list_f2)

print (all_vlans - vlan_list_f1) & (all_vlans - vlan_list_f2)

