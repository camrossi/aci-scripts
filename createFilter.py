__author__ = 'camrossi'


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import cobra.model.vz
from cobra.internal.codec.xmlcodec import toXMLStr

import argparse
import yaml


def get_args():
    parser = argparse.ArgumentParser(description="Configure Filter")
    parser.add_argument('-d', dest='delete', help='delete the config', action='store_true')
    parser.add_argument('-f', dest='file', help='Filter Config in YAML format')
    args = parser.parse_args()
    return args


# Get command line arguments
args = get_args()

# open yaml files
f = open('credentials_fab2.yaml', 'r')
credentials = yaml.load(f)
f.close()

f = open(args.file, 'r')
config = yaml.load(f)
f.close()

# list of packages that should be imported for this code to work

# log into an APIC and create a directory object

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'])
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made

topMo = cobra.model.pol.Uni('')

fvTenant = cobra.model.fv.Tenant(topMo, config['Tenant'])

# build the request using cobra syntax
tcp = False
udp = False

vzFilterTCP = cobra.model.vz.Filter(fvTenant, ownerKey=u'', name= config['Filter_name'] + '-TCP-Flt', descr=u'', ownerTag=u'')
vzFilterUDP = cobra.model.vz.Filter(fvTenant, ownerKey=u'', name= config['Filter_name'] + '-UDP-Flt', descr=u'', ownerTag=u'')

for entry in config['Entries']:
    if 'tcp' in entry['proto']:
        vzEntry = cobra.model.vz.Entry(vzFilterTCP, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=entry['ToDestPort'], descr=u'', matchDscp=u'unspecified', prot=u'tcp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=entry['stateful'], icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=entry['FromDestPort'], name=entry['name'])
        tcp = True
    if 'udp' in entry['proto']:
        vzEntry = cobra.model.vz.Entry(vzFilterUDP, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=entry['ToDestPort'], descr=u'', matchDscp=u'unspecified', prot=u'udp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=entry['stateful'], icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=entry['FromDestPort'], name=entry['name'])
        udp = True

#If we do not have any UPD or TCP entried delete the FLT Object as is empty
if not tcp:
    vzFilterTCP.delete()
if not udp:
    vzFilterUDP.delete()

# commit the generated code to APIC
print toXMLStr(fvTenant)
c = cobra.mit.request.ConfigRequest()
c.addMo(fvTenant)
md.commit(c)

