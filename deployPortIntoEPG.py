__author__ = 'camrossi'

#This script assumes that you have already configured a port and you just need to map it to an EPG.
#Useful for "trunk" type of interfacews when we need to dump a port in hundreds of already existing EPGs

import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.model.vns
import cobra.mit.naming
import yaml
import argparse
import warnings
from cobra.internal.codec.xmlcodec import toXMLStr
warnings.filterwarnings("ignore")


def get_args():
    parser = argparse.ArgumentParser(description="Configure NetScaler")
    parser.add_argument('-d', dest='delete', help='delete the config', action='store_true')
    parser.add_argument('-f', dest='file', help='NetScaler Config in YAML format')
    args = parser.parse_args()
    return args


def get_path(switches, int_type, interface):

    if int_type in ['vpc', 'vPC', 'VPC']:
        path = 'topology/pod-1/protpaths-' + switches + '/pathep-[' + interface + ']'
    elif int_type in ['pc', 'PC']:
        path = 'topology/pod-1/paths-' + str(switches) + '/pathep-[' + interface + ']'
    else:
        path = 'topology/pod-1/paths-' + str(switches) + '/pathep-[eth' + interface + ']'

    rspathAtt = '/rspathAtt-[' + path + ']'

    return path, rspathAtt


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


for epg in config['epgs']:
    for switch in config['switches']:
        for interface in config['interfaces']:
            path, rspathAtt= get_path(switch, config['interface_type'], interface)

            topDn = cobra.mit.naming.Dn.fromString('uni/tn-' + config['tenant'] + '/ap-' + config['application'] + '/epg-' + epg['name'] + rspathAtt)
            topParentDn = topDn.getParent()
            topMo = md.lookupByDn(topParentDn)

            # build the request using cobra syntax
            RsPathAtt = cobra.model.fv.RsPathAtt(topMo, mode=config['mode'], instrImedcy='lazy', encap=epg['encap'], tDn=path)

            if args.delete:
                RsPathAtt.delete()


            # commit the generated code to APIC
            print toXMLStr(topMo)
            c = cobra.mit.request.ConfigRequest()
            c.addMo(topMo)
            md.commit(c)
