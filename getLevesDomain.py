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
import getpass


warnings.filterwarnings("ignore")

# Parse command line arguments
def get_args():
    parser = argparse.ArgumentParser(description="Return the mapping between leaves and phy Domains")
    #Get a list of nodes
    parser.add_argument('-l', dest='leaves', nargs = '*', help=' Leaves ID as a comma separatedlist 101,102,103')
    parser.add_argument('-u', dest='user', help='APIC Username')
    parser.add_argument('-a', dest='apic', help='APIC Address')



    args = parser.parse_args()
    return args

args= get_args()
aci_password = getpass.getpass()


ls = cobra.mit.session.LoginSession(args.apic,args.user, aci_password, secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print 'Logging in to ' + args.apic
md.login()

# Get node list
print 'Getting Node Lis'
q = cobra.mit.request.DeploymentQuery('phys-ccp_aci_cni_cluster_1-pdom')
# grab the childrens as well
q.subtree = 'full-deployment'
q.subtreeClassFilter = 'pconsNodeDeployCtx'

mos = md.query(q)

for i in mos:
    pprint(i)
