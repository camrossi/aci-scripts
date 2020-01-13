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
    parser.add_argument('-f', dest='filter', help='Filter Name', type=str)
    args = parser.parse_args()
    return args


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



# Get all the contracts in the fabric
q = cobra.mit.request.ClassQuery('vzBrCP')
q.subtree = 'full'

# From the subtree return only the child that are of class vzRsSubjFiltAtt --> relationship between filter ans subject
q.subtreeClassFilter = 'vzRsSubjFiltAtt'

# Return only the Subjects that are using one of the filters that are matching the port we need.
# Basicaly we check that the DN of the vzRsSubjFiltAtt contains the name of the filter. That means that we do get back all the contracts
# however only the one that match our filter have a subject attached
q.subtreePropFilter = 'wcard(vzRsSubjFiltAtt.dn, "{}")'.format(args.filter)
# Run the query
contracts = md.query(q)

for contract in contracts:
    # If the returned contract has a subject
    if contract.subj:
        for subjects in contract.subj:
            for flt in subjects.rssubjFiltAtt:
                print "\t {}".format(str(flt.dn).strip('/uni'))
        # print "\n"


