# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.naming
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import yaml
from cobra.internal.codec.xmlcodec import toXMLStr
import warnings
import ipaddress

warnings.filterwarnings("ignore")

# open yaml files
f = open('credentials_camfab.yaml', 'r')
credentials = yaml.load(f)
f.close()

num_epgs = 1000
ipv4_attr_per_epg = 1000
vmm_domain = u'uni/vmmp-VMware/dom-ACI'

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False,
                                    timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()

print 'Generating config'

# the top level object on which operations will be made
# Confirm the dn below is for your top dn
ip_addr = u'1.0.0.0'
ip_addr = ipaddress.IPv4Address(u'1.0.0.0')

c = cobra.mit.request.ConfigRequest()
topMo = md.lookupByDn('uni/tn-uSeg/ap-uSeg')

for n in range(1, num_epgs):
    print n
    epg_name = 'uSeg' + str(n)
    # build the request using cobra syntax
    fvAEPg = cobra.model.fv.AEPg(topMo, isAttrBasedEPg=u'yes', matchT=u'AtleastOne', name=epg_name, descr=u'',
                                 fwdCtrl=u'', prefGrMemb=u'exclude', nameAlias=u'', prio=u'unspecified',
                                 pcEnfPref=u'unenforced')
    fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg, tDn=vmm_domain, netflowDir=u'both', epgCos=u'Cos0', classPref=u'encap',
                                         primaryEncap=u'unknown', delimiter=u'', instrImedcy=u'immediate',
                                         resImedcy=u'immediate', encap=u'unknown', encapMode=u'auto',
                                         netflowPref=u'disabled', epgCosPref=u'disabled')
    fvRsCustQosPol = cobra.model.fv.RsCustQosPol(fvAEPg, tnQosCustomPolName=u'')
    fvRsBd = cobra.model.fv.RsBd(fvAEPg, tnFvBDName=u'BD1')
    fvCrtrn = cobra.model.fv.Crtrn(fvAEPg, ownerKey=u'', name=u'default', descr=u'', prec=u'0', nameAlias=u'',
                                   ownerTag=u'', match=u'any')
    fvCrtrn = cobra.model.fv.Crtrn(fvAEPg, ownerKey=u'', name=u'default', descr=u'', prec=u'0', nameAlias=u'',
                                   ownerTag=u'', match=u'any')
    for i in range(1, ipv4_attr_per_epg):
        # print ip_addr
        ip_addr = ipaddress.IPv4Address(ip_addr) + 1
        fvIpAttr = cobra.model.fv.IpAttr(fvCrtrn, ownerKey=u'', name=i, descr=u'', ip=ip_addr, nameAlias=u'',
                                         ownerTag=u'', usefvSubnet=u'no')

    #    fvAEPg.delete()
    c.addMo(topMo)

    # commit the generated code to APIC, the post are too big so I am splitting them out in
    # 50 EPGs with 1000 IPv4 addresses each
    if n > 0 and n % 50 == 0:
        print('Commit {}/{}').format(n, num_epgs)
        md.commit(c)
        c = cobra.mit.request.ConfigRequest()
        topMo = md.lookupByDn('uni/tn-uSeg/ap-uSeg')
        print('Commint Done')