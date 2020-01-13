# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.mit.naming
from cobra.internal.codec.xmlcodec import toXMLStr

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession('https://10.67.40.128', 'admin', 'C1sc0123456')
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
# Confirm the dn below is for your top dn
topDn = cobra.mit.naming.Dn.fromString('uni/tn-Camillo/ap-nVGRE_AppP/epg-nVGRE_EPG')
topParentDn = topDn.getParent()
topMo = md.lookupByDn(topParentDn)

# build the request using cobra syntax
fvAEPg = cobra.model.fv.AEPg(topMo, prio=u'unspecified', matchT=u'AtleastOne', name=u'nVGRE_EPG', descr=u'')
fvRsAEPgMonPol = cobra.model.fv.RsAEPgMonPol(fvAEPg, tnMonEPGPolName=u'default')
fvRsPathAtt = cobra.model.fv.RsPathAtt(fvAEPg, instrImedcy=u'immediate', mode=u'regular', encap=u'vlan-602', tDn=u'topology/pod-1/paths-101/pathep-[eth1/25]')
fvRsPathAtt2 = cobra.model.fv.RsPathAtt(fvAEPg, instrImedcy=u'immediate', mode=u'regular', encap=u'vlan-603', tDn=u'topology/pod-1/paths-101/pathep-[eth1/27]')
fvRsPathAtt3 = cobra.model.fv.RsPathAtt(fvAEPg, instrImedcy=u'lazy', mode=u'untagged', encap=u'vlan-608', tDn=u'topology/pod-1/paths-102/pathep-[eth1/25]')
fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg, instrImedcy=u'lazy', tDn=u'uni/phys-Camillo_PhyDom', resImedcy=u'lazy')
fvRsDomAtt2 = cobra.model.fv.RsDomAtt(fvAEPg, instrImedcy=u'lazy', tDn=u'uni/vmmp-VMware/dom-VMM', resImedcy=u'lazy')
fvRsBd = cobra.model.fv.RsBd(fvAEPg, tnFvBDName=u'nVGRE_BD')
fvRsCustQosPol = cobra.model.fv.RsCustQosPol(fvAEPg, tnQosCustomPolName=u'default')
fvRsProv = cobra.model.fv.RsProv(fvAEPg, tnVzBrCPName=u'HTTP_HTTPS', matchT=u'AtleastOne', prio=u'unspecified')


# commit the generated code to APIC
print toXMLStr(topMo)
c = cobra.mit.request.ConfigRequest()
c.addMo(topMo)
md.commit(c)