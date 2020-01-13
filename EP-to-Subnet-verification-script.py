__author__ = 'camrossi'


import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.model.vns
import cobra.mit.naming
import yaml
import ipaddress
import argparse
import warnings
import prettytable
from cobra.internal.codec.xmlcodec import toXMLStr
warnings.filterwarnings("ignore")


def get_args():
    parser = argparse.ArgumentParser(description="Verify the learned EP IP is contained in the BD Subnet")
    parser.add_argument('-e', dest='EPG', help='EPG Name')
    parser.add_argument('-1', dest='App', help='Application Name')
    parser.add_argument('-t', dest='Tenant', help='Tenant Name')
    args = parser.parse_args()
    return args


bds_dict = {}


def get_l3_bds_and_epgs(md, epg_dn):
    # GET ALL THE EPs for the specified epgs

    q = cobra.mit.request.ClassQuery('fvBD')
    # I need the full subtree as I need to go deeper than 1 acl.
    q.subtree = 'full'
    q.propFilter = 'eq(fvBD.unicastRoute, "yes")'

    # Only need these 2 classes The node blocks and the PortProfiles NO SPACE after the comma!!!
    q.subtreeClassFilter = 'fvSubnet,fvRtBd'

    # Get all the switch profiles
    BDs = md.query(q)
    for bd in BDs:
        bd_dn = str(bd.dn)
        bds_dict[bd_dn] = {'Subnets':[], 'EPGs': {}}
        # subnets = (s for s in bd.children if 'fvSubnet' in s)
        for items in bd.children:
            if isinstance(items, cobra.modelimpl.fv.subnet.Subnet):
                # print(items.ip)
                bds_dict[bd_dn]['Subnets'].append(items.ip)
        for items in bd.children:
            if isinstance(items, cobra.modelimpl.fv.rtbd.RtBd):
                get_EPG_EPs(items.tDn, bd_dn)
        # print('\n')

def get_EPG_EPs(epg_dn, bd_dn):
    q = cobra.mit.request.DnQuery(epg_dn)
    q.subtree = 'full'
    q.subtreeClassFilter = 'fvCEp'
    epgs = md.query(q)
    for epg in epgs:
        # print(bds_dict[bd_dn]['EPGs'])
        for ep in epg.children:
            if str(epg.dn) not in bds_dict[bd_dn]['EPGs']:
                bds_dict[bd_dn]['EPGs'][str(epg.dn)] = []

            #Discard Host that do not have an IP
            if '0.0.0.0' != str(ep.ip):
                bds_dict[bd_dn]['EPGs'][str(epg.dn)].append(str(ep.ip))
            # print (bds_dict)

def check_ep_bd_subnet(eps, bd_subnets):
    pass



# Get command line arguments
args = get_args()

# open yaml files
f = open('credentials_fab2.yaml', 'r')
credentials = yaml.load(f)
f.close()


# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()

get_l3_bds_and_epgs(md, None)

# pprint(bds_dict)

output = prettytable.PrettyTable(['EPG', 'BD', 'Subnets', "EPs"])
output.align = 'l'
misconfigured_ep = {}
for bd in bds_dict:
    print("Processing BD {0}").format(bd)
    if len(bds_dict[bd]['Subnets']) == 0:
        print("WARNING This BD has no subnets defined but unicast routing is enabled")
    for epg in bds_dict[bd]['EPGs']:
        for subnet in bds_dict[bd]['Subnets']:
            # print(epg)
            for ip in bds_dict[bd]['EPGs'][epg]:
                # print("{0}  {1}").format(ip,subnet)
                if ipaddress.IPv4Address(unicode(ip)) not in ipaddress.IPv4Network(unicode(subnet), strict=False):
                    print('The {0} IP under EPG {1} BD {2} is not contained in the BD subnet {3}').format(ip, epg, bd, subnet)
                    # print (subnet)
                    if epg not in misconfigured_ep:
                        misconfigured_ep[epg] = set()
                    misconfigured_ep[epg].add(ip)
                # else:
                #     print("All the EP in EPG {0} are contained in the BD Subnets").format(epg)
        if epg in misconfigured_ep:
            output.add_row([epg, bd, ', '.join(bds_dict[bd]['Subnets']), ', '.join(misconfigured_ep[epg])])
        misconfigured_ep = {}
    print('\n')

print("Summary")

print(output)
