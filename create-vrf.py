# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import cobra.model.vz
from cobra.internal.codec.xmlcodec import toXMLStr

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession('https://10.67.40.128', 'apic#apdcnlab\\fabric1', 'Cisco.123')
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
polUni = cobra.model.pol.Uni('')
fvTenant = cobra.model.fv.Tenant(polUni, 'ACI_FAB1_POD7')

# build the request using cobra syntax
for i in range(1,3):
    fvCtx = cobra.model.fv.Ctx(fvTenant, ownerKey='', name='VRF-' + str(i), descr='567')
    fvRsBgpCtxPol = cobra.model.fv.RsBgpCtxPol(fvCtx, tnBgpCtxPolName='')
    fvRsCtxToExtRouteTagPol = cobra.model.fv.RsCtxToExtRouteTagPol(fvCtx, tnL3extRouteTagPolName='')
    fvRsOspfCtxPol = cobra.model.fv.RsOspfCtxPol(fvCtx, tnOspfCtxPolName='')
    vzAny = cobra.model.vz.Any(fvCtx, matchT='AtleastOne', name='', descr='', prefGrMemb='disabled')
    fvRsCtxToEpRet = cobra.model.fv.RsCtxToEpRet(fvCtx, tnFvEpRetPolName='')

# commit the generated code to APIC
# print toXMLStr(fvTenant)
    c = cobra.mit.request.ConfigRequest()
    c.addMo(fvTenant)
    print md.commit(c)
