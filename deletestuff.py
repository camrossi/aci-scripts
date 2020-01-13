__author__ = 'camrossi'
__author__ = 'camrossi'


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fvns
import cobra.model.infra
import cobra.model.pol
from cobra.internal.codec.xmlcodec import toXMLStr
import yaml

f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()


q = cobra.mit.request.ClassQuery('infraNodeP')

#I select only my tenat base on the name
# q.propFilter='eq(fvTenant.name, "Camillo")'

# I need the full subtree as I need to go deeper than 1 acl.
q.subtree = 'full'

# Only need the EPG class
# q.subtreeClassFilter = 'fvAEPg'

result = md.query(q)

polUni = cobra.model.pol.Uni('')
infraInfra = cobra.model.infra.Infra(polUni)
infraFuncP = cobra.model.infra.FuncP(infraInfra)

for object in result:
    c = cobra.mit.request.ConfigRequest()
    polUni = cobra.model.pol.Uni('')
    if object.name is not None:
        print object.name
        dom = cobra.model.infra.NodeP(infraInfra, ownerKey='', name=object.name, descr='', ownerTag='')
        dom.delete()
        c.addMo(infraInfra)
        md.commit(c)
        # time.sleep(5)





    # fvTenant = cobra.model.fv.Tenant(polUni, tenant.name)
    # for application in tenant.children:
    #     print application.name
    #     fvAp = cobra.model.fv.Ap(fvTenant, application.name)
    #     for epg in application.children:
    #         print epg.name
    #         fvAEPg = cobra.model.fv.AEPg(fvAp, epg.name)
    #         #Map the domain to the EPG
    #         fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg, instrImedcy='lazy', resImedcy='lazy', encap='unknown', tDn='uni/phys-camrossi_phydom')
    #         # fvRsDomAtt.delete()
    #         c.addMo(fvAEPg)
