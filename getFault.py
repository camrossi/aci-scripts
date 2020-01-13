import argparse
import re
import cobra.mit.access
import cobra.mit.session
from prettytable import PrettyTable
import warnings
import yaml

warnings.filterwarnings("ignore")

f = open('credentials_fab1.yaml', 'r')
credentials = yaml.load(f)
f.close()

ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'],
                                    secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print 'Logging in to ' + credentials['host']
md.login()

# Get node list
print 'Getting Faults '
q = cobra.mit.request.ClassQuery('fltCnts')
# q.propFilter='eq(faultInst.code, "F1298")'

mos = md.query(q)


print len(mos)
