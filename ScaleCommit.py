#!/usr/bin/env python


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.mit.naming
import yaml
import argparse
from cobra.internal.codec.xmlcodec import toXMLStr
import warnings
warnings.filterwarnings("ignore")


class ConfigRequest(cobra.mit.request.ConfigRequest):

    #check BDs count only demo code

    def addMo(self, mo):
        q = cobra.mit.request.ClassQuery('fvBD')
        q.subtreeInclude = 'count'
        count = md.query(q)
        print((count[0].count))
        if (int(count[0].count)) > 300 :
            print("too many BDs, stopping the execution")
            exit()

        cobra.mit.request.ConfigRequest.addMo(self,mo)

            #
        # q = cobra.mit.request.ClassQuery('ctxClassCnt')
        # q.subtreeClassFilter = 'l2BD'
        # count = md.query(q)
        # print((count))

    # super(cobra.mit.request.ConfigRequest)


def get_args():
    parser = argparse.ArgumentParser(description="Configure BD")
    parser.add_argument('-d', dest='delete', help='delete the config', action='store_true')
    parser.add_argument('-f', dest='file', help='BD Config in YAML format')
    args = parser.parse_args()
    return args


def expand_vlan_range(vlans):
    vlans_numbers = []
    for vlan in vlans:
        vlan = str(vlan)
        if '-' in vlan:
            a, b = vlan.split('-')
            a, b = int(a), int(b)
            vlans_numbers.extend(range(a, b + 1))
        else:
            vlans_numbers.append(int(vlan))
    return vlans_numbers

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

tenant = 'uni/tn-' + config['tenant']
vlans = expand_vlan_range(config['vlans'])
for vlan in vlans:
    print(vlan)
    bd_name = 'V' + str(vlan) +'_BD'
    ctx_name =  config['ctx']
    topBD = cobra.mit.naming.Dn.fromString(tenant + '/BD-' + bd_name)
    topParentDn = topBD.getParent()
    topMo = md.lookupByDn(topParentDn)
    fvBD = cobra.model.fv.BD(topMo, unkMacUcastAct=config['unkUcast'], unkMcastAct='flood', name=bd_name,
                             descr='', arpFlood=config['arpFlood'], unicastRoute=config['unicastRoute'])
    # print toXMLStr(fvBD)
    fvRsCtx = cobra.model.fv.RsCtx(fvBD, tnFvCtxName=ctx_name)
    # print toXMLStr(fvRsCtx)
    if args.delete:
        fvBD.delete()
    # commit the generated code to APIC
    # print toXMLStr(topMo)
    c = ConfigRequest()
    # c.check_scale()
    c.addMo(topMo)
    md.commit(c)