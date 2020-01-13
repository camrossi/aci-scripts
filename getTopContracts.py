__author__ = 'camrossi'


#!/usr/bin/env python
#
# Written by Toru Okatsu @ Cisco Systems, August 20th 2014
#
# Modified by Camillo Rossi @ Cisco Systems, February 2015
#

import argparse
from pprint import pprint
import re
import cobra.mit.access
import cobra.mit.session
from prettytable import PrettyTable
import warnings
import yaml

warnings.filterwarnings("ignore")



# Parse command line arguments
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

print 'Logging in to ' + credentials['host']
md.login()

print 'Load all Filters'
q = cobra.mit.request.ClassQuery('vzFilter')
# q.propFilter='eq(vzFilter.name, "tn-ZS_TAFE")'
q.subtree = 'children'
q.subtreeClassFilter= 'vzEntry'
filters = md.query(q)


print 'Getting Contracts'
q = cobra.mit.request.ClassQuery('vzBrCP')
# q.propFilter='eq(vzBrCP.name, "ZS_CON_NONPROD_AD")'
q.propFilter='wcard(vzBrCP.dn, "tn-ZS_TAFE")'

q.subtree = 'full'

contracts_usage = []
mos = md.query(q)
nodes = {}
# flt = (item for item in filters if item.dn == "uni/tn-ZS_TAFE/flt-ZS_FIL_NONPROD_TIBCO_AMX_MGMT").next()
# print len(list(flt.children))
for mo in mos:
    # print "Contract ", mo.dn
    cons = 0
    prov = 0
    entries = 0
    for child in mo.children:
        if type(child) is cobra.model.vz.Subj:
            # print child.dn
            #Iterate over the children of a Subject --> (vzRsSubjFiltAtt) to get the dn of the bloody filter
            for vzRsSubjFiltAtt in child.children:
                if type(vzRsSubjFiltAtt) is cobra.model.vz.RsSubjFiltAtt:
                    # print("\t {}").format(vzRsSubjFiltAtt.tDn)
                    try:
                        flt = (item for item in filters if item.dn == vzRsSubjFiltAtt.tDn).next()
                    except StopIteration:
                        pass
                    entries += len(list(flt.children))
        if type(child) is cobra.model.vz.RtCons:
            cons += 1
        if type(child) is cobra.model.vz.RtProv:
            prov += 1
    contracts_usage.append({'name':str(mo.dn).split('-')[2], 'cons': cons,'prov': prov,
                            'entries':entries, 'tcam': (cons * prov * entries *2)})

tcam = 0
for i in contracts_usage:
    tcam += i['tcam']

print("Top 10 TCAM Consumer")
for i in sorted(contracts_usage, key=lambda k: k['tcam'], reverse=True)[0:9]:
    print("\t{} is consuming {} TCAM entries.").format(i['name'], i['tcam'])
    print("\t \t is provided by {} and consumed by {} EPGs").format(i['prov'], i['cons'])

print("\nTop 10 consumed contracts (you should consider vzAny)")
for i in sorted(contracts_usage, key=lambda k: k['cons'], reverse=True)[0:9]:
    print("\t{} is consumed by {}, provided by {} and is using {} entries.").format(i['name'], i['cons'], i['prov'], i['entries'])
    print("\t\tEstimated TCAM usage: {}").format(i['tcam'])

print("\nTop 10 provided contracts (you should consider vzAny)")
for i in sorted(contracts_usage, key=lambda k: k['prov'], reverse=True)[0:9]:
    print("\t{} is provided by {}, consumed by {} and is using {} entries.").format(i['name'], i['prov'], i['cons'], i['entries'])
    print("\t\tEstimated TCAM usage: {}").format(i['tcam'])

print("Worst case (all contract needed on a leaf) TCAM usage {}:").format(tcam)
