__author__ = 'camrossi'
# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.vns
import cobra.mit.naming
from cobra.internal.codec.xmlcodec import toXMLStr

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession('https://10.67.40.128', 'admin', 'C1sc0123456')
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
# Confirm the dn below is for your top dn
topDn = cobra.mit.naming.Dn.fromString('uni/tn-Camillo/lDevVip-VPX-Cluster')
topParentDn = topDn.getParent()
topMo = md.lookupByDn(topParentDn)

# build the request using cobra syntax
vnsLDevVip = cobra.model.vns.LDevVip(topMo,  name='VPX-Cluster',   devtype='VIRTUAL',  contextAware='single-Context', mode='legacy-Mode', funcType='GoTo')
vnsCCred = cobra.model.vns.CCred(vnsLDevVip, name='username', value='nsroot')
vnsRsMDevAtt = cobra.model.vns.RsMDevAtt(vnsLDevVip, tDn='uni/infra/mDev-Citrix-NetScaler-1.0')
vnsCCredSecret = cobra.model.vns.CCredSecret(vnsLDevVip, name='password', value='nsroot')
vnsCMgmt = cobra.model.vns.CMgmt(vnsLDevVip, name='', host='10.67.40.138', port='80')
vnsRsALDevToDomP = cobra.model.vns.RsALDevToDomP(vnsLDevVip, tDn='uni/vmmp-VMware/dom-VMM')
vnsDevFolder = cobra.model.vns.DevFolder(vnsLDevVip,  name='enableFeature',   key='enableFeature')
vnsDevParam = cobra.model.vns.DevParam(vnsDevFolder,  value='ENABLE', name='LB',   key='LB')
vnsDevParam = cobra.model.vns.DevParam(vnsDevFolder,  value='ENABLE', name='SSL',   key='SSL')
vnsCDev = cobra.model.vns.CDev(vnsLDevVip, name='VPX-Cluster_Device_1', devCtxLbl='',    vcenterName='ACI-vCenter', vmName='camrossi-NSVPX-1')
vnsCCred2 = cobra.model.vns.CCred(vnsCDev, name='username', value='nsroot')
vnsCCredSecret2 = cobra.model.vns.CCredSecret(vnsCDev, name='password', value='nsroot')
vnsCMgmt2 = cobra.model.vns.CMgmt(vnsCDev, name='', host='10.67.40.140', port='80')
vnsCIf = cobra.model.vns.CIf(vnsCDev, name='0_1', vnicName='Network adapter 1')
vnsCIf2 = cobra.model.vns.CIf(vnsCDev, name='1_1', vnicName='Network adapter 2')
vnsCDev2 = cobra.model.vns.CDev(vnsLDevVip, name='VPX-Cluster_Device_2', devCtxLbl='',    vcenterName='ACI-vCenter', vmName='camrossi-NSVPX-2')
vnsCCred3 = cobra.model.vns.CCred(vnsCDev2, name='username', value='nsroot')
vnsCCredSecret3 = cobra.model.vns.CCredSecret(vnsCDev2, name='password', value='nsroot')
vnsCMgmt3 = cobra.model.vns.CMgmt(vnsCDev2, name='', host='10.67.40.141', port='80')
vnsCIf3 = cobra.model.vns.CIf(vnsCDev2, name='0_1', vnicName='Network adapter 1')
vnsCIf4 = cobra.model.vns.CIf(vnsCDev2, name='1_1', vnicName='Network adapter 2')
vnsLIf = cobra.model.vns.LIf(vnsLDevVip, name='mgmt')
vnsRsMetaIf = cobra.model.vns.RsMetaIf(vnsLIf, tDn='uni/infra/mDev-Citrix-NetScaler-1.0/mIfLbl-mgmt')
vnsRsCIfAtt = cobra.model.vns.RsCIfAtt(vnsLIf, tDn='uni/tn-Camillo/lDevVip-VPX-Cluster/cDev-VPX-Cluster_Device_1/cIf-[0_1]')
vnsRsCIfAtt2 = cobra.model.vns.RsCIfAtt(vnsLIf, tDn='uni/tn-Camillo/lDevVip-VPX-Cluster/cDev-VPX-Cluster_Device_2/cIf-[0_1]')
vnsLIf2 = cobra.model.vns.LIf(vnsLDevVip, name='external')
vnsRsMetaIf2 = cobra.model.vns.RsMetaIf(vnsLIf2, tDn='uni/infra/mDev-Citrix-NetScaler-1.0/mIfLbl-outside')
vnsRsCIfAtt3 = cobra.model.vns.RsCIfAtt(vnsLIf2, tDn='uni/tn-Camillo/lDevVip-VPX-Cluster/cDev-VPX-Cluster_Device_2/cIf-[1_1]')
vnsRsCIfAtt4 = cobra.model.vns.RsCIfAtt(vnsLIf2, tDn='uni/tn-Camillo/lDevVip-VPX-Cluster/cDev-VPX-Cluster_Device_1/cIf-[1_1]')
vnsLIf3 = cobra.model.vns.LIf(vnsLDevVip, name='internal')
vnsRsMetaIf3 = cobra.model.vns.RsMetaIf(vnsLIf3, tDn='uni/infra/mDev-Citrix-NetScaler-1.0/mIfLbl-inside')
vnsRsCIfAtt5 = cobra.model.vns.RsCIfAtt(vnsLIf3, tDn='uni/tn-Camillo/lDevVip-VPX-Cluster/cDev-VPX-Cluster_Device_2/cIf-[1_1]')
vnsRsCIfAtt6 = cobra.model.vns.RsCIfAtt(vnsLIf3, tDn='uni/tn-Camillo/lDevVip-VPX-Cluster/cDev-VPX-Cluster_Device_1/cIf-[1_1]')


# commit the generated code to APIC
print toXMLStr(topMo)
c = cobra.mit.request.ConfigRequest()
c.addMo(topMo)
md.commit(c)