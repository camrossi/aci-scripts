__author__ = 'camrossi'


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.modelimpl.fv.cep
import cobra.model.pol
import yaml
import warnings
import time

warnings.filterwarnings("ignore")


f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()

# Get all EPGs
q = cobra.mit.request.ClassQuery('fvAEPg')
# Get the children
q.subtree = 'children'

#Get only EPGs from the proper tenant. 
q.propFilter='wcard(fvAEPg.dn, "uni/tn-KubeSpray")'

#Of the Children get on the Client End Point and VMM Domain
q.subtreeClassFilter = 'fvCEp,fvRsDomAtt'

result = md.query(q)

polUni = cobra.model.pol.Uni('')
c = 0
for epg in result:
    has_ep = False
    for i in epg.children:
        #check if I have EP attached
        if isinstance(i ,cobra.modelimpl.fv.cep.CEp):
            has_ep = True
    if has_ep:
       print("EPG {} has endpoint, skipping").format(epg.name)
    else:
        for i in epg.children:
            if type(i) is cobra.modelimpl.fv.rsdomatt.RsDomAtt and i.tCl == "vmmDomP":
                print("Deleting VMM Domain {} from EGP {}").format(i.tDn, epg.name)
               
               #CHECK THE ABOVE OUTPUT FIRST!!!! Then Uncomment this is the actual config push

                c = cobra.mit.request.ConfigRequest()
                q2 = cobra.mit.request.DnQuery(i.dn)
                vmm = md.query(q2)
                vmm[0].delete()
                c.addMo(vmm[0])
                md.commit(c)
                c=+1

print('Deleted {} VMM Domains').format(c)
