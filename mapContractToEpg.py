# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.mit.naming
from cobra.internal.codec.xmlcodec import toXMLStr
import warnings
import yaml
import argparse
warnings.filterwarnings("ignore")

def get_args():
    parser = argparse.ArgumentParser(description="Configure BD")
    parser.add_argument('-d', dest='delete', help='delete the config', action='store_true')
    parser.add_argument('-f', dest='file', help='BD Config in YAML format')
    args = parser.parse_args()
    return args

# Get command line arguments
args = get_args()

# open yaml files
f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()

f = open(args.file, 'r')
config = yaml.load(f)
f.close()

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()

for c_name in config['prov_cont']:
    topDn = cobra.mit.naming.Dn.fromString('uni/tn-' + config['tenant'] + '/ap-' + config['application'] + '/epg-' + config['epg'] + '/rsprov-' + c_name)
    topParentDn = topDn.getParent()
    topMo = md.lookupByDn(topParentDn)

    # PROVIDED CONTRACT
    cobra.model.fv.RsProv(topMo, tnVzBrCPName=c_name, matchT='AtleastOne', prio='unspecified')
    if args.delete:
        topMo.delete()
    # commit the generated code to APIC
    print toXMLStr(topMo)
    c = cobra.mit.request.ConfigRequest()
    c.addMo(topMo)
    md.commit(c)

for c_name in config['cons_cont']:
    topDn = cobra.mit.naming.Dn.fromString('uni/tn-' + config['tenant'] + '/ap-' + config['application'] + '/epg-' + config['epg'] + '/rsprov-' + c_name)
    topParentDn = topDn.getParent()
    topMo = md.lookupByDn(topParentDn)

    # CONSUMED CONTRACT
    cobra.model.fv.RsCons(topMo, tnVzBrCPName=c_name, prio='unspecified')
    if args.delete:
        topMo.delete()
    # commit the generated code to APIC
    print toXMLStr(topMo)
    c = cobra.mit.request.ConfigRequest()
    c.addMo(topMo)
    md.commit(c)