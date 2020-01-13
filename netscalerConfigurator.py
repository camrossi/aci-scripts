__author__ = 'camrossi'
#
# Written by Camillo Rossi @ Cisco System February 2015
#!/usr/bin/env python
# list of packages that should be imported for this code to work

import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.model.vns
import cobra.mit.naming
import yaml
import argparse
import warnings
from netscaler import NetScaler
warnings.filterwarnings("ignore")


def get_args():
    parser = argparse.ArgumentParser(description="Configure NetScaler")
    parser.add_argument('-d', dest='delete', help='delete the config', action='store_true')
    parser.add_argument('-f', dest='file', help='NetScaler Config in YAML format')
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

topDn = cobra.mit.naming.Dn.fromString('uni/tn-' + config['tenant'] + '/ap-' + config['application'] + '/epg-' + config['epg'])
topParentDn = topDn.getParent()
topMo = md.lookupByDn(topParentDn)
#GET EPG
fvAEPg = cobra.model.fv.AEPg(topMo, matchT=u'AtleastOne', name=unicode(config['epg']), descr=u'', prio=u'unspecified')

# The constructor take ctrctName, graphName, nodeName, fvAEPg, topMo, md (I commit the changes from the netscaler class. Not sure is the best way

ns = NetScaler(config['ctrctName'], config['graphName'], config['nodeName'], fvAEPg, topMo, md)

if not args.delete:
    if 'nsips' in config:
        for nsip in config['nsips']:
            ns.add_ip(nsip['name'], nsip['ip'], nsip['mask'])
    #
    # # ## YOU MUST ADD THE IP AND THEN THE ROUTES OR THE CONFIGURATION WILL FAIL TO APPLY TO THE NETSCALER!!!
    #
    if 'routes' in config:
        for route in config['routes']:
            ns.add_route(route['name'], route['ip'], route['mask'], route['gw'])

    if 'vips' in config:
        for vip in config['vips']:
            ns.add_vip(vip['name'], vip['ip'], vip['port'])

    if 'sgs' in config:
        for sg in config['sgs']:
            ns.add_service_group(sg['name'], sg['port'])

    if 'server_to_sg' in config:
        for sgs in config['server_to_sg']:
            for sg, servers in sgs.items():
                for server in servers:
                    ns.add_server_to_service_group(sg, server['name'],server['ip'])

    if 'sgs_vips' in config:
        for sgs_vips in config['sgs_vips']:
            ns.map_sg_vip(sgs_vips['sg_name'], sgs_vips['vip_name'])

elif args.delete:
    if 'nsips' in config:
        for nsip in config['nsips']:
            ns.remove_ip(nsip['name'])

    if 'routes' in config:
        for route in config['routes']:
            ns.remove_route(route['name'])

    if 'vips' in config:
        for vip in config['vips']:
            ns.remove_vip(vip['name'])

    if 'sgs' in config:
        for sg in config['sgs']:
            ns.remove_service_group(sg['name'])

    if 'server_to_sg' in config:
        for sgs in config['server_to_sg']:
            for sg, servers in sgs.items():
                for server in servers:
                    ns.remove_server_from_service_group(sg, server['name'], server['ip'])

    if 'sgs_vips' in config:
        for sgs_vips in config['sgs_vips']:
            ns.unmap_sg_vip(sgs_vips['sg_name'], sgs_vips['vip_name'])
