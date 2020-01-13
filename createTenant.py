# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import cobra.model.vz
from cobra.internal.codec.xmlcodec import toXMLStr
import yaml
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Configure BD")
    parser.add_argument('-d', dest='delete', help='delete the config', action='store_true')
    parser.add_argument('-f', dest='file', help='BD Config in YAML format')
    args = parser.parse_args()
    return args


# Get command line arguments
args = get_args()

# open yaml files
f = open('credentials_fab2.yaml', 'r')
credentials = yaml.load(f)
f.close()

# f = open(args.file, 'r')
# config = yaml.load(f)
# f.close()

FAB = u'1'
# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()


# the top level object on which operations will be made
polUni = cobra.model.pol.Uni('')

for i in range(1,11):
    name = u'ACI_FAB' + FAB + u'_POD' + str(i)
    bd = u'BD-' + str(i)
    vrf = u'VRF-' + str(i)
    print(name)
    # build the request using cobra syntax
    fvTenant = cobra.model.fv.Tenant(polUni, ownerKey=u'', name=name, descr=u'', ownerTag=u'')
    fvBD = cobra.model.fv.BD(fvTenant, ownerKey=u'', vmac=u'not-applicable', name=bd, descr=u'', unkMacUcastAct=u'proxy', arpFlood=u'no', limitIpLearnToSubnets=u'no', llAddr=u'::', epMoveDetectMode=u'', unicastRoute=u'yes', ownerTag=u'', multiDstPktAct=u'bd-flood', unkMcastAct=u'flood')
    fvRsBDToNdP = cobra.model.fv.RsBDToNdP(fvBD, tnNdIfPolName=u'')
    fvRsCtx = cobra.model.fv.RsCtx(fvBD, tnFvCtxName=vrf)
    fvRsIgmpsn = cobra.model.fv.RsIgmpsn(fvBD, tnIgmpSnoopPolName=u'')
    fvRsBdToEpRet = cobra.model.fv.RsBdToEpRet(fvBD, resolveAct=u'resolve', tnFvEpRetPolName=u'')
    fvCtx = cobra.model.fv.Ctx(fvTenant, ownerKey=u'', name=vrf, descr=u'', knwMcastAct=u'permit', pcEnfDir=u'ingress', ownerTag=u'', pcEnfPref=u'enforced')
    fvRsBgpCtxPol = cobra.model.fv.RsBgpCtxPol(fvCtx, tnBgpCtxPolName=u'')
    fvRsCtxToExtRouteTagPol = cobra.model.fv.RsCtxToExtRouteTagPol(fvCtx, tnL3extRouteTagPolName=u'')
    fvRsOspfCtxPol = cobra.model.fv.RsOspfCtxPol(fvCtx, tnOspfCtxPolName=u'')
    vzAny = cobra.model.vz.Any(fvCtx, matchT=u'AtleastOne', name=u'', descr=u'')
    fvRsCtxToEpRet = cobra.model.fv.RsCtxToEpRet(fvCtx, tnFvEpRetPolName=u'')
    fvRsTenantMonPol = cobra.model.fv.RsTenantMonPol(fvTenant, tnMonEPGPolName=u'')
    # commit the generated code to APIC
    c = cobra.mit.request.ConfigRequest()
    c.addMo(fvTenant)
    md.commit(c)



