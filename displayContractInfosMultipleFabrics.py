#!/usr/bin/env python
#fchis scrip will look up a contract by DN and provide the EPGs using it as well as the port that are utilised by the contract.
#list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.mit.naming
from pprint import pprint
import prettytable
import warnings
import json
import yaml
import sys
import datetime
from getpass import getpass
from urllib.parse import urlparse 
warnings.filterwarnings("ignore")
# User credentials
# Insert one controller per site
apic_controllers = [ 'https://fab2-apic1.cam.ciscolabs.com' ]
apic_user = input("Enter your APIC username: ") 
apic_pass = getpass()
todays_date = datetime.date.today()
for hostname in apic_controllers:
    # log into an APIC and create a directory object
    ls = cobra.mit.session.LoginSession(hostname, apic_user, apic_pass,secure=False, timeout=180)
    md = cobra.mit.access.MoDirectory(ls)
    md. login()
    parse_hostname = urlparse(hostname) 
    hostname = parse_hostname.hostname
    #Qury the APIC to get Con/Pro/Subjects and inherited EPG info for this contract
    ql = cobra.mit.request.ClassQuery('vzBrCP') 
    ql.subtree = 'full'
    ql.subtreeClassFilter ='vzRtCons,vzRtProv,vzSubj,vzInheritedDef,vzRsSubjFiltAtt,vzRtAnyToProv,vzRtIf,vzRtAnyToCons,vzIntDef'
    # Run the query
    contracts = md.query(ql) 
    for contract in contracts:
    # Clear lists
        consumer_epgs = []
        provider_epgs = [] 
        config_filters = []
        exported_contracts = []
        for child in contract.children:
            if type(child) is cobra.model.vz.RtCons:
                consumer_epgs.append(child.tDn)
            if type(child) is cobra.model.vz.RtProv:
                provider_epgs.append(child.tDn)
            if type(child) is cobra.model.vz.RtAnyToCons:
                consumer_epgs.append('vzAny ==> ' + child. tDn + ' <== vzAny')
            if type(child) is cobra.model.vz.RtAnyToProv:
                provider_epgs.append('vzAny ==> ' + child. tDn + ' <== vzAny')
            if type(child) is cobra.model.vz.RtIf: #Exported contracts
                exported_contracts.append(child.tDn)
                q2 = cobra.mit.request.DnQuery(child.tDn) 
                q2. subtree = "children"
                q2. subtreeClassFilter = 'vzRtConsIf,vzRtAnyToConsIf'
                exp_contracts = md. query(q2)
                for exp_contract in exp_contracts:
                    for child in exp_contract.children:
                        consumer_epgs.append(child.tDn) 
            if type(child) is cobra.model.vz.InheritedDef:
                for epg in child.children:
                    if type(epg) is cobra.model.vz.ProvDef:
                        provider_epgs.append(epg.epgDn)
                    if type(epg) is cobra.model.vz.ConsDef: 
                        consumer_epgs.append(epg.epgDn)
            if type(child) is cobra.model.vz.Subj: 
                for SubjFiltAtt in child.children:
                    if type(SubjFiltAtt) is cobra.model.vz.RsSubjFiltAtt:
                        q2 = cobra.mit.request.DnQuery(SubjFiltAtt.tDn)
                        q2.subtree = "children"
                        q2.subtreeClassFilter = 'vzEntry'
                        filters = md.query(q2)
                        for fit in filters:
                            for e in fit.children:
                                config_filters.append({"Prot":e. prot, "sFromPort":e. sFromPort, "sToPort": e.sToPort,"dFromPort": e.dFromPort, "dToPort": e.dToPort})

        output = prettytable. PrettyTable(['Consumer EPGs', 'Provider EPGs ', 'Ports'])
        output.align = 'l'
        output.add_row(['\n'.join(consumer_epgs), '\n'.join(provider_epgs), json.dumps(config_filters, indent=1,sort_keys=True)])
        
        #print(output)
        if len(exported_contracts) > 0:
            output2 = prettytable.PrettyTable(['Contract', 'Exported Contracts'])
            output2.align = 'l'

            output2.add_row([str(contract.dn), '\n'.join(exported_contracts)])
         #   print(output2)
        filename = "%s_%s_%s" % (todays_date, hostname, contract. name) 
        with open(filename, "w") as f:
            f.write(str(output))
            if len(exported_contracts) > 0:
                f.write("\n")
                f.write(str(output2))
