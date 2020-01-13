# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import cobra.model.vmm
from cobra.internal.codec.xmlcodec import toXMLStr

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession('https://fab1-apic1.cam.ciscolabs.com', 'admin', '123Cisco123')
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
polUni = cobra.model.pol.Uni('')
fvTenant = cobra.model.fv.Tenant(polUni, 'SeviceGraphs')
fvAp = cobra.model.fv.Ap(fvTenant, 'SG_App1')

# build the request using cobra syntax
c = cobra.mit.request.ConfigRequest()
for i in range(1,201):
    name = 'BE' + str(i)
    fvAEPg = cobra.model.fv.AEPg(fvAp, isAttrBasedEPg=u'no', matchT=u'AtleastOne', name=name, descr=u'', fwdCtrl=u'', prefGrMemb=u'exclude', nameAlias=u'', prio=u'unspecified', pcEnfPref=u'unenforced')
    fvRsProv = cobra.model.fv.RsProv(fvAEPg, tnVzBrCPName=u'App1_EXT_FE_TO_BE', matchT=u'AtleastOne', prio=u'unspecified')
    fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg, tDn=u'uni/vmmp-VMware/dom-ACI', primaryEncap=u'unknown', classPref=u'encap', delimiter=u'', instrImedcy=u'immediate', encap=u'unknown', encapMode=u'auto', netflowPref=u'disabled', resImedcy=u'immediate')
    vmmSecP = cobra.model.vmm.SecP(fvRsDomAtt, ownerKey=u'', name=u'', descr=u'', forgedTransmits=u'reject', nameAlias=u'', ownerTag=u'', allowPromiscuous=u'reject', macChanges=u'reject')
    fvRsCustQosPol = cobra.model.fv.RsCustQosPol(fvAEPg, tnQosCustomPolName=u'')
    fvRsBd = cobra.model.fv.RsBd(fvAEPg, tnFvBDName=u'App1_BE_BD')
    fvAEPg.delete()
    c.addMo(fvAEPg)

md.commit(c)


# commit the generated code to APIC
# print toXMLStr(fvAp)
