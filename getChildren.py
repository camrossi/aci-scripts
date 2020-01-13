import argparse
import re
import cobra.mit.access
import cobra.mit.session
import yaml

f = open('credentials_camfab.yaml', 'r')
credentials = yaml.load(f)
f.close()


ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'],
                                    secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print 'Logging in to ' + credentials['host']
md.login()
# Get node list
print 'Getting Contracts'
q = cobra.mit.request.ClassQuery('fvTenant')
q.ClassFilter = 'Camillo'
q.subtree = 'children'

Tenants = md.query(q)

class_set = set()
for Tenant in Tenants:
    for child in Tenant.children:
        class_set.add(type(child))

for c in class_set:
    print c