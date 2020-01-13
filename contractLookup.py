#!/usr/bin/env python

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.mit.naming
import yaml
import argparse
import warnings
warnings.filterwarnings("ignore")

def get_args():
    parser = argparse.ArgumentParser(description="Looking for a ports in filter. Return the contract using the filter")
    parser.add_argument('-p', dest='port', help='TCP/UDP port', type=int)
    args = parser.parse_args()
    return args

# since some of the port values are encoded as string I need to map them back to the port interger value
def port_to_int(port):
    port_map = {'unspecified':0, 'https':443, 'http':80, 'smtp':25, 'ftpData':21, 'dns':53, 'pop3':110,'rtsp':554}
    try:
        return int(port)
    except:
        return port_map[port]




# Get command line arguments
args = get_args()

# open yaml files with the credentials
f = open('credentials_camfab.yaml', 'r')
credentials = yaml.load(f)
f.close()


# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()

#Qury the APIC for all the filters
q = cobra.mit.request.ClassQuery('vzFilter')
q.subtree = 'children'
# Run the query
filters = md.query(q)

flt_list = ""

#iterate over the filters
for filt in filters:
    # print filt.dn
    # "uni/tn-common/flt-arp/e-arp" ==> E-arp == Entry
    # iterate over the ACLs
    for acl in filt.e:
        # get the filter name withiht the "E" class preposition
        flt_name = filt.name.split('/e-')[0]
        if port_to_int(acl.sFromPort) <= args.port <= port_to_int(acl.sToPort):
            flt_list += flt_name + '|'
            break
        if port_to_int(acl.dFromPort) <= args.port <= port_to_int(acl.dToPort) :
            flt_list += flt_name + '|'

#Remove the trailing | character
flt_list = flt_list[:-1]


# Get all the contracts in the fabric
q = cobra.mit.request.ClassQuery('vzBrCP')
q.subtree = 'full'

# From the subtree return only the child that are of class vzRsSubjFiltAtt --> relationship between filter ans subject
q.subtreeClassFilter = 'vzRsSubjFiltAtt'

# Return only the Subjects that are using one of the filters that are matching the port we need.
# Basicaly we check that the DN of the vzRsSubjFiltAtt contains the name of the filter. That means that we do get back all the contracts
# however only the one that match our filter have a subject attached
q.subtreePropFilter = 'wcard(vzRsSubjFiltAtt.dn, "{}")'.format(flt_list)
# Run the query
contracts = md.query(q)

for contract in contracts:
    # If the returned contract has a subject
    if contract.subj:
        print("Contract {} is using the following filter matching the port".format(str(contract.dn).strip('/uni')))
        for subjects in contract.subj:
            for flt in subjects.rssubjFiltAtt:
                print("\t {}".format(str(flt.dn).strip('/uni')))
        print("\n")


