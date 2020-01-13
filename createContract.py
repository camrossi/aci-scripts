# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.vz
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


# the top level object on which operations will be made
# Confirm the dn below is for your top dn

for c_name in config['cont_name']:
    topDn = cobra.mit.naming.Dn.fromString('uni/tn-' + config['tenant'] + '/brc-' + c_name)
    topParentDn = topDn.getParent()
    topMo = md.lookupByDn(topParentDn)

    # build the request using cobra syntax
    vzBrCP = cobra.model.vz.BrCP(topMo, ownerKey='', name=c_name, prio='unspecified', descr='', ownerTag='')
    vzSubj = cobra.model.vz.Subj(vzBrCP, revFltPorts='yes', name='Permit_All', prio='unspecified', descr='', consMatchT='AtleastOne', provMatchT='AtleastOne')
    vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, tnVzFilterName=config['filter'])

    if args.delete:
        topMo.delete()
    # commit the generated code to APIC
    print toXMLStr(topMo)
    c = cobra.mit.request.ConfigRequest()
    c.addMo(topMo)
    md.commit(c)
