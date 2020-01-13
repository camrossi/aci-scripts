__author__ = 'camrossi'

# list of packages that should be imported for this code to work
import yaml
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.l3ext
import cobra.model.pol
from cobra.internal.codec.xmlcodec import toXMLStr

f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'])
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
polUni = cobra.model.pol.Uni('')
fvTenant = cobra.model.fv.Tenant(polUni, 'Camillo')
l3extOut = cobra.model.l3ext.Out(fvTenant, 'ERN-1')
l3extInstP = cobra.model.l3ext.InstP(l3extOut, 'ExtNet1')

subnet_list = ['192.168.1.0/24', '192.168.2.0/24', '192.168.3.0/24', '192.168.4.0/24',
               '192.168.5.0/24', '192.168.6.0/24', '192.168.7.0/24', '192.168.8.0/24',
               '192.168.9.0/24', '192.168.10.0/24', '192.168.11.0/24', '192.168.12.0/24',
               '192.168.13.0/24', '192.168.14.0/24', '192.168.15.0/24', '192.168.16.0/24',
               '192.168.17.0/24', '192.168.18.0/24', '192.168.19.0/24']

# build the request using cobra syntax
for s in subnet_list:
    l3extSubnet = cobra.model.l3ext.Subnet(l3extInstP, name='', descr='', ip=s, aggregate='', scope='export-rtctrl,import-security')

    # IF you want to delete uncomment the line below
    # l3extSubnet = cobra.model.l3ext.Subnet(l3extInstP, name='', descr='', ip=s, aggregate='').delete()


# commit the generated code to APIC

c = cobra.mit.request.ConfigRequest()
c.addMo(l3extInstP)
md.commit(c)
#
# for i in range(1,20):
#     print "'192.168.'" + str(i) + "'.0/24',"