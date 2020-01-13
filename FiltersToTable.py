__author__ = 'camrossi'

# From filter XML generates a CSV with FIleter name entries and filter details.
# Could be improved

import xmltodict
import re

with open('/Users/camrossi/Downloads/Filters.xml') as fd:
    obj = xmltodict.parse(fd.read())


filter_dic = {}
# print obj['imdata']['vzFilter']['vzEntry'].keys()

for filter in obj['imdata']['vzEntry']:
    # print filter
    # Search for a workd that start with flt- that is the name of the fileter
    # the DN would look like "uni/tn-MCS_Admin/flt-MCS_Admin_To_L3_Out/e-LDAP
    m = re.search('(?<=flt-)\w+', filter['@dn'])
    if not filter_dic.has_key(m.group(0)):
        filter_dic[m.group(0)] = set()
    filter_dic[m.group(0)].add(str(filter["@name"] + ', ' + filter["@prot"] + ', ' + filter["@dFromPort"] + ', ' + filter["@dToPort"]))

print "Filter Name, Entries, Protocol, From, To"
for key, set in filter_dic.items():
    print key + ',,,,'
    for elem in set:
        print ',' + elem





