__author__ = 'camrossi'


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import yaml

f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()


q = cobra.mit.request.ClassQuery('fvTenant')

#I select only my tenat base on the name
q.propFilter='eq(fvTenant.name, "ZS_TAFE")'

# I need the full subtree as I need to go deeper than 1 acl.
q.subtree = 'full'

# Only need the EPG class
q.subtreeClassFilter = 'fvRsPathAtt'

result = md.query(q)

polUni = cobra.model.pol.Uni('')
c = cobra.mit.request.ConfigRequest()
for tenant in result:
    print tenant.name
    fvTenant = cobra.model.fv.Tenant(polUni, tenant.name)
    for application in tenant.children:
        print application.name
        fvAp = cobra.model.fv.Ap(fvTenant, application.name)
        for epg in application.children:
            fvAEPg = cobra.model.fv.AEPg(fvAp, epg.name)
            for fvRsPathAtt in epg.children:
                fvRsPathAtt.delete()
                c.addMo(fvRsPathAtt)
            #Map the domain to the EPG
#            fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg, instrImedcy='immediate', resImedcy='immediate', encap='unknown', tDn='uni/phys-ZS_PHY_DOM_ASR')
 #           fvRsDomAtt.delete()
 #           c.addMo(fvAEPg)
md.commit(c)
