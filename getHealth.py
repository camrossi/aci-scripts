import cobra.mit.access
import cobra.mit.session
import warnings
import yaml

warnings.filterwarnings("ignore")

f = open('credentials_camfab.yaml', 'r')
credentials = yaml.load(f)
f.close()

ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'],
                                    secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print 'Logging in to ' + credentials['host']
md.login()

dn= 'uni/tn-MultiCast/ap-LiveBroadcast/epg-Source/health'

#'Getting Health '
dnQuery = cobra.mit.request.DnQuery(dn)
healthMo = md.query(dnQuery)

print "The current healt of {} is {}".format(dn, healthMo[0].cur)
