#!/usr/bin/env python
#
# Written by Toru Okatsu @ Cisco Systems, August 20th 2014
#
# Modified by Camillo Rossi @ Cisco Systems, February 2015
#

import argparse
import cobra.mit.access
import cobra.mit.session
import warnings
import yaml
import json
from prettytable import PrettyTable
import socket
import pyexcel


warnings.filterwarnings("ignore")


def get_args():
    parser = argparse.ArgumentParser(description="Get EPG information of each node")
    parser.add_argument('-p', dest='ports', nargs = '*', help='Port 1/1')
    parser.add_argument('-n', dest='nodes', nargs = '*', help='Node Number')
    parser.add_argument('-e', dest='epgs', nargs = '*', help='EPG name i.e. Tenant:App:EPG')

    args = parser.parse_args()
    return args


# Main function

# Get command line arguments
args = get_args()

# Login to the APIC and create the directory object

f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()


ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'],
                                    secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print('Logging in to ' + credentials['host'])
md.login()

# Get node list
print('Getting Interfaces')

q = cobra.mit.request.ClassQuery('topSystem')
q.propFilter='eq(topSystem.role, "leaf")'

# grab the childrens as well
q.subtree = 'full'
q.subtreeClassFilter = 'l1PhysIf,epmMacEp,epmRtMacEpToIpEpAtt'
#grab only the class l2RsPathDomAtt from the cildrens
# q.subtreeClassFilter = 'pcAggrMbrIf'

leaves = md.query(q)

output = PrettyTable(['Node','Mac and Port', 'ip'])

for leaf in leaves:
    first_leaf = True
    # for c in leaf.children:
    #     print c.rn

    for a in leaf.ctx:
        for b in a.bd:
            for c in b.vlan:
                for d in c.db:
                    for mac in d.mac:
                        k= str(mac.rn) + " " + str(mac.ifId)
                        mac_to_ip = {k:[]}
                        for ip in mac.rsmacEpToIpEpAtt:
                            ip_addr = str(ip.rn).split("ip")[1].strip("-[]")
                            mac_to_ip[k].append(ip_addr)
                    for mac_addr in mac_to_ip:
                        if first_leaf:
                            output.add_row([leaf.name, mac_addr, ', '.join(mac_to_ip[mac_addr])])
                            first_leaf = False
                        else:
                            output.add_row(["", mac_addr, ', '.join(mac_to_ip[mac_addr])])


print output

# q = cobra.mit.request.ClassQuery('compVNic')
# vmnics = md.query(q)
#
# for vmnic in vmnics:
#         print vmnic.mac, vmnic.ip
#
#

# print socket.gethostbyaddr("10.66.183.51")
