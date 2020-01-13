__author__ = 'camrossi'

#!/usr/bin/env python
#
# Written by Mike Timm @ cisco System, March 2014
# Revised by Toru Okatsu @ Cisco Systems, June 11th 2014
# Modified by Camillo Rossi to return only some port on a specific node

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import argparse
from prettytable import PrettyTable
import warnings
import sys
import yaml

def expand_port_range(ports):
    result = []
    port_numbers = []
    for port in ports:
        if '-' not in port:
            result.append(port)
        else:
            for part in port.split('/'):
                if '-' not in part:
                    m = part
                if '-' in part:
                    a, b = part.split('-')
                    a, b = int(a), int(b)
                    port_numbers.extend(range(a, b + 1))
            for i in port_numbers:
                result.append(m + '/' + str(i))
    return result

########
# Main #
########

warnings.filterwarnings("ignore")

#Load Credentials
f = open('credentials_camfab.yaml', 'r')
credentials = yaml.load(f)
f.close()

# Set up arg parse

parser = argparse.ArgumentParser()
parser.add_argument("-n", nargs = '*', help='List of Node ID')
parser.add_argument("-p", nargs = '*', help='List of Port x/y or x/y-z')
args = parser.parse_args()


output = PrettyTable(['Node/Port','admin','Usage', 'Neg', 'speed',  'Oper Status','Oper Status Reason','Channeling'])

# log into an APIC and create a directory object

ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
print('Logging in to ' + credentials['host'])
md.login()


#Port Parser
port_list = expand_port_range(args.p)

print('Looking up interfaces')
for n in args.n:
    for p in port_list:
        int_dn_phys = 'topology/pod-1/node-' + n + '/sys/phys-[eth' + p + ']'
        #print int_dn_phys
        int_dn_ethpmPhysIf = int_dn_phys + '/phys'
        int_channeling = int_dn_phys + '/aggrmbrif'
        node_port = n + ' ' + p

        #poor man progress bar. Need to flush all the time or you see the dots only at the end.
        sys.stdout.write('.')
        sys.stdout.flush()

        int = md.lookupByDn(int_dn_phys)
        pint = md.lookupByDn(int_dn_ethpmPhysIf)
        channel = md.lookupByDn(int_channeling)
        output.add_row([node_port, int.adminSt, int.usage, int.autoNeg, int.speed, pint.operSt,  pint.operStQual, channel.channelingSt])

print('')
print(output)