import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.mit.naming
from cobra.internal.codec.xmlcodec import toXMLStr
import warnings
import argparse
import yaml
import time


warnings.filterwarnings("ignore")



def get_args():
    parser = argparse.ArgumentParser(description="Flush all End Points under a BD")
    parser.add_argument('-b', dest='bd', help='Bridge Domain Name', default='MCS_Admin_Infra')
    parser.add_argument('-t', dest='tenant', help='Tenant Name', default='MCS_Admin')
    args = parser.parse_args()
    return args

args = get_args()

# open yaml files
f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
# Confirm the dn below is for your top dn
tdn_uri = 'uni/tn-' + args.tenant + '/BD-' + args.bd
topDn = cobra.mit.naming.Dn.fromString(tdn_uri)
topParentDn = topDn.getParent()
topMo = md.lookupByDn(topParentDn)

print 'Disabled L2 Unknow Proxy (this flushes all the EP) on ' + tdn_uri
# build the request using cobra syntax
fvBD = cobra.model.fv.BD(topMo, ownerKey='', name=args.bd, descr='', unkMacUcastAct='flood', arpFlood='no', mac='00:22:BD:F8:19:FF', unicastRoute='yes', ownerTag='', unkMcastAct='flood')


# commit the generated code to APIC
#print toXMLStr(topMo)
c = cobra.mit.request.ConfigRequest()
c.addMo(topMo)
md.commit(c)


print 'Sleep for 5 second zzzzz....'
time.sleep(5)
fvBD = cobra.model.fv.BD(topMo, ownerKey='', name=args.bd, descr='', unkMacUcastAct='proxy', arpFlood='no', mac='00:22:BD:F8:19:FF', unicastRoute='yes', ownerTag='', unkMcastAct='flood')


# commit the generated code to APIC
#print toXMLStr(topMo)
c = cobra.mit.request.ConfigRequest()
c.addMo(topMo)
md.commit(c)
print 'Enabled  L2 Unknow Proxy on ' + tdn_uri
print 'Done goodbye!'
