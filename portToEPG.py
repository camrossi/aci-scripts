#!/usr/bin/env python
#
# Written by Toru Okatsu @ Cisco Systems, August 20th 2014
#
# Modified by Camillo Rossi @ Cisco Systems, February 2015
#

import argparse
import re
import cobra.mit.access
import cobra.mit.session
from prettytable import PrettyTable
import warnings
import yaml

warnings.filterwarnings("ignore")

# This class is to store EPG and port information on the node
class Node:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.epg_table = {}
        self.port_table = {}

    def has_epg(self, epg):
        return self.epg_table.has_key(epg)

    def add_epg(self, epg):
        self.epg_table[epg] = set()

    def add_port(self, epg, port, encap):
        port = port[3:]
        #drop eth from the port name
        if not self.has_epg(epg):
            self.add_epg(epg)
        if not self.port_table.has_key(port):
            self.port_table[port] = set()

        self.epg_table[epg].add(port)
        self.port_table[port].add(epg + " " + encap)
        # self.port_table[port].add(encap)

    def get_epgs(self):
        return self.epg_table

    def get_ports(self):
        return self.port_table

    def get_port(self,port):
        if self.port_table.has_key(port):
            return self.port_table[port]
        else:
            return None


# Parse command line arguments
def get_args():
    parser = argparse.ArgumentParser(description="Get EPG information of each node")
    parser.add_argument('-p', dest='ports', nargs = '*', help='Port 1/1')
    parser.add_argument('-n', dest='nodes', nargs = '*', help='Node Number')
    parser.add_argument('-e', dest='epgs', nargs = '*', help='EPG name i.e. Tenant:App:EPG')

    args = parser.parse_args()
    return args

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

# Get the node id and port id from tDn of l2RsPathDomAtt class
# Ex. topology/pod-1/node-103/sys/conng/path-[eth1/31]
def get_path(dn):
    m = re.search('/node\-(\d+)/.+/path-\[(eth[\d/]+)\]', str(dn))
    if m:
        return (m.group(1), m.group(2))
    else:
        return (None, None)

def add_epg_to_output_table(node_key,port_key, epg_set, output):
    epg_str = ''
    c = 0
    l = len(epg_set)

    for epg in epg_set:
        c += 1
        if c == l:
            epg_str += epg
        else:
            epg_str += epg + '\n'

    output.add_row([node_key + '/' + port_key, epg_str])


def print_node_port_epg():
    output = PrettyTable(['Node/Port', 'EPGs / encap'])
    output.align = 'l'
    if args.nodes and args.ports:
        for node_key in args.nodes:
            if node_key in nodes:
                for port_key in args.ports:
                    epg_set = nodes[node_key].get_port(port_key)
                    if epg_set:
                        add_epg_to_output_table(node_key, port_key, epg_set, output)
                    else:
                        output.add_row([node_key + '/' + port_key, 'No EPG Mapping'])

    elif args.nodes and not args.ports:
        for node_key in args.nodes:
            if node_key in nodes:
                ports = nodes[node_key].get_ports()
                for port, epg_set in sorted(ports.items()):
                        add_epg_to_output_table(node_key, port, epg_set, output)

    elif args.ports and not args.nodes:
        for key, node in sorted(nodes.items()):
            for port_key in args.ports:
                epg_set = node.get_port(port_key)
                if epg_set:
                    add_epg_to_output_table(node.id, port_key, epg_set, output)
                else:
                    output.add_row([node.id + '/' + port_key, 'No EPG Mapping'])

    else: # Print everythig the result
        for key, node in sorted(nodes.items()):
            ports = node.get_ports()
            for port, epg_set in sorted(ports.items()):
                add_epg_to_output_table(node.id, port, epg_set, output)

    print output


def print_node_epg_port():
    output = PrettyTable(['EPGs', 'Node', 'Port'])
    output.align = 'l'
    for node in nodes:
        port_list = ''
        epg_table = nodes[node].get_epgs()
        for epg in args.epgs:
            c = 0
            if epg in epg_table:
                for port in epg_table[epg]:
                    c += 1
                    if c == 10:
                        c = 0
                        port_list += port + '\n'
                    else:
                        port_list += port + ' '
                output.add_row([epg, node, port_list])
    print output

# Main function

# Get command line arguments
args = get_args()
if args.ports:
    args.ports = expand_port_range(args.ports)
# Login to the APIC and create the directory object

f = open('credentials_camfab.yaml', 'r')
credentials = yaml.load(f)
f.close()


ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'],
                                    secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)

print 'Logging in to ' + credentials['host']
md.login()

# Get node list
print 'Getting Node Lis'
q = cobra.mit.request.ClassQuery('fabricNode')
mos = md.query(q)
nodes = {}
for mo in mos:
    if mo.role == 'leaf':
        nodes[mo.id] = Node(mo.id, mo.name)

print 'Getting vlanCktEp'
q = cobra.mit.request.ClassQuery('vlanCktEp')
# grab the childrens as well
q.subtree = 'children'
#grab only the class l2RsPathDomAtt from the cildrens
q.subtreeClassFilter = 'l2RsPathDomAtt'

#this quesry returns the EPs and the l2RsPathDomAtt acl.
print 'Getting l2RsPathDomAtt acl of vlanCktEp'
eps = md.query(q)

print 'Bulding Dictionaries'

for ep in eps:
    if ep.encap != 'unknown':
        for child in ep.rspathDomAtt:
            #the TOP Dn contains the port and node ID. topology/pod-1/node-101/sys/conng/path-[eth1/33]
            (node, port) = get_path(child.tDn)
            if node:
                nodes[node].add_port(ep.name, port, ep.encap)

# Show port to EPG Mapping
if args.nodes or args.ports:
    print_node_port_epg()

#Show EPG to port mapping
if args.epgs:
    print_node_epg_port()
