#!/usr/bin/env python3

#this scrip will look up a contract by DN and provide the EPGs using it as well as the port that are utilised by the contract. 

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.mit.naming
import yaml
import json
import argparse
from pprint import pprint
import prettytable
import warnings
warnings.filterwarnings("ignore")

def get_args():
    parser = argparse.ArgumentParser(description="Looking for a ports in filter. Return the contract using the filter")
    parser.add_argument('-c', dest='contract_dn', help='contract DN i.e. uni/tn-Tenant/brc-contract')
    args = parser.parse_args()
    return args

# Get command line arguments
args = get_args()

# open yaml files with the credentials
f = open('credentials_camfab.yaml', 'r')
credentials = yaml.load(f)
f.close()

consumer_epgs = []
provider_epgs = []
config_filters = []
exported_contracts = []

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()


#Qury the APIC to get Con/Pro/Subjects and inherited EPG info for this contract 
q1 = cobra.mit.request.DnQuery(args.contract_dn)
q1.subtree = 'full'
q1.subtreeClassFilter = 'vzRtCons,vzRtProv,vzSubj,vzInheritedDef,vzRsSubjFiltAtt,vzRtAnyToProv,vzRtAnyToCons,vzIntDef,vzRtIf'
# Run the query
contracts = md.query(q1)
for contract in contracts:
    for child in contract.children:
        if type(child) is cobra.model.vz.RtCons:
            consumer_epgs.append(child.tDn)
        if type(child) is cobra.model.vz.RtProv:
            provider_epgs.append(child.tDn)
        if type(child) is cobra.model.vz.RtAnyToCons:
            consumer_epgs.append(child.tDn)
        if type(child) is cobra.model.vz.RtAnyToProv:
            provider_epgs.append('vzAny ==> ' + child.tDn + '<== vzAny')
        if type(child) is cobra.model.vz.RtIf: #Exported contracts
            exported_contracts.append(child.tDn)
            q2 = cobra.mit.request.DnQuery(child.tDn)
            q2.subtree = "children"
            q2.subtreeClassFilter = 'vzRtConsIf'
            exp_contracts = md.query(q2)
            for exp_contract in  exp_contracts:
                 for child in exp_contract.children:
                     consumer_epgs.append(child.tDn)
        if type(child) is cobra.model.vz.InheritedDef:
            for epg in child.children:
                if type(epg) is cobra.model.vz.ProvDef:
                    provider_epgs.append(epg.epgDn)
                if type(epg) is cobra.model.vz.ConsDef:
                    consumer_epgs.append(epg.epgDn)
        if type(child) is  cobra.model.vz.Subj:
            for SubjFiltAtt in child.children:
                q2 = cobra.mit.request.DnQuery(SubjFiltAtt.tDn)
                q2.subtree = "children"
                q2.subtreeClassFilter = 'vzEntry'
                filters = md.query(q2)
                for flt in filters:
                   for e in flt.children:
                      config_filters.append({"Prot":e.prot,"sFromPort":e.sFromPort,"sToPort": e.sToPort,"dFromPort": e.dFromPort, "dToPort": e.dToPort})


output = prettytable.PrettyTable(['Consumer EPGs', 'Provider EPGs', 'Ports'])
output.align = 'l'

output.add_row(['\n'.join(consumer_epgs),'\n'.join(provider_epgs),json.dumps(config_filters, indent=1,sort_keys=True)])
print(output)


output = prettytable.PrettyTable(['Contract', 'Exported Contracts'])
output.align = 'l'

output.add_row([args.contract_dn, '\n'.join(exported_contracts)])

print(output)
