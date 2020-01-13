# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.naming
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.vns
from cobra.internal.codec.xmlcodec import toXMLStr

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession('https://fab1-apic1.cam.ciscolabs.com', 'admin', '123Cisco123')
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
# Confirm the dn below is for your top dn
topDn = cobra.mit.naming.Dn.fromString('uni/tn-ManagedModeSG/ap-App1/epg-Server')
topParentDn = topDn.getParent()
topMo = md.lookupByDn(topParentDn)

# build the request using cobra syntax
fvAEPg = cobra.model.fv.AEPg(topMo, isAttrBasedEPg=u'no', matchT=u'AtleastOne', name=u'Server', descr=u'', fwdCtrl=u'', prefGrMemb=u'exclude', nameAlias=u'', prio=u'unspecified', pcEnfPref=u'unenforced')
for i in range(1,21):
    print i
    lbvserver = u'lbvserver' + str(100 + i)
    VIP = u'VIP'  + str(100 + i)
    VIP_IP = u'192.168.255.' + str(100 + i)
    vnsFolderInst = cobra.model.vns.FolderInst(fvAEPg, locked=u'no', graphNameOrLbl=u'VPX', devCtxLbl=u'', ctrctNameOrLbl=u'VPX-ALL', scopedBy=u'epg', nodeNameOrLbl=u'N1', key=u'lbvserver', cardinality=u'unspecified', nameAlias=u'', name=lbvserver)
    vnsParamInst = cobra.model.vns.ParamInst(vnsFolderInst, validation=u'', mandatory=u'no', name=u'servicetype', nameAlias=u'', value=u'HTTP', key=u'servicetype', locked=u'no', cardinality=u'unspecified')
    vnsParamInst2 = cobra.model.vns.ParamInst(vnsFolderInst, validation=u'', mandatory=u'no', name=u'name', nameAlias=u'', value=VIP, key=u'name', locked=u'no', cardinality=u'unspecified')
    vnsParamInst3 = cobra.model.vns.ParamInst(vnsFolderInst, validation=u'', mandatory=u'no', name=u'lbmethod', nameAlias=u'', value=u'LEASTCONNECTION', key=u'lbmethod', locked=u'no', cardinality=u'unspecified')
    vnsParamInst4 = cobra.model.vns.ParamInst(vnsFolderInst, validation=u'', mandatory=u'no', name=u'port', nameAlias=u'', value=u'80', key=u'port', locked=u'no', cardinality=u'unspecified')
    vnsParamInst5 = cobra.model.vns.ParamInst(vnsFolderInst, validation=u'', mandatory=u'no', name=u'ipv46', nameAlias=u'', value=VIP_IP, key=u'ipv46', locked=u'no', cardinality=u'unspecified')
    vnsFolderInst2 = cobra.model.vns.FolderInst(vnsFolderInst, locked=u'no', graphNameOrLbl=u'VPX', devCtxLbl=u'', ctrctNameOrLbl=u'VPX-ALL', scopedBy=u'epg', nodeNameOrLbl=u'N1', key=u'lbvserver_servicegroup_binding', cardinality=u'unspecified', nameAlias=u'', name=u'lbvserver_servicegroup_binding')
    vnsCfgRelInst = cobra.model.vns.CfgRelInst(vnsFolderInst2, mandatory=u'no', name=u'servicename', nameAlias=u'', key=u'servicename', locked=u'no', cardinality=u'unspecified', targetName=u'SG100')
    vnsFolderInst3 = cobra.model.vns.FolderInst(fvAEPg, locked=u'no', graphNameOrLbl=u'VPX', devCtxLbl=u'', ctrctNameOrLbl=u'VPX-ALL', scopedBy=u'epg', nodeNameOrLbl=u'N1', key=u'mFCnglbvserver', cardinality=u'unspecified', nameAlias=u'', name=u'mFCnglbvserver101')
    vnsCfgRelInst2 = cobra.model.vns.CfgRelInst(vnsFolderInst3, mandatory=u'no', name=u'lbvserver_key', nameAlias=u'', key=u'lbvserver_key', locked=u'no', cardinality=u'unspecified', targetName=lbvserver)

    vnsFolderInst.delete()

    # commit the generated code to APIC
    print toXMLStr(topMo)
    c = cobra.mit.request.ConfigRequest()
    c.addMo(topMo)
    md.commit(c)
