__author__ = 'camrossi'

# This script will return a list of all the port that are configured in a int sel profile
# and the mapping to a switch selector.

import cobra.mit.access
import cobra.mit.session
import argparse
from prettytable import PrettyTable
import warnings
import yaml

#Define how to call a non existing switch ID. It is a key in a dictionary so can be anything.
NAN = 'OrphanPorts'

###########
# Classes #
###########


class Node:
    def __init__(self, id):
        self.id = id
        self.port_set = set()
        self.switch_profile_dic = {}

    def has_profile(self, pfl):
        return pfl in self.switch_profile_dic

    def add_profile(self, pfl):
        self.switch_profile_dic[pfl] = set()

    def add_port(self, port, switch_profile):
        self.port_set.add(port)
        if not self.has_profile(switch_profile):
            self.add_profile(switch_profile)
        self.switch_profile_dic[switch_profile].add(port)

    def get_sorted_ports(self):      # sort by module number and then port number
        return sorted(self.port_set, key=lambda port:(int(port.split('/')[0]), int(port.split('/')[1])), reverse=True)

    def get_port_per_sw_pfl(self):
        return self.switch_profile_dic


def get_nodes_port_data():

    warnings.filterwarnings("ignore")
    #Load Credentials
    f = open('credentials_pwc.yaml', 'r')
    credentials = yaml.load(f)
    f.close()

    ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
    md = cobra.mit.access.MoDirectory(ls)
    print 'Logging in to ' + credentials['host']
    md.login()

    # GET ALL THE Switch Profiles

    q = cobra.mit.request.ClassQuery('infraNodeP')
    # I need the full subtree as I need to go deeper than 1 acl.
    q.subtree = 'full'
    # q.propFilter()

    # Only need these 2 classes The node blocks and the PortProfiles
    q.subtreeClassFilter = 'infraNodeBlk,infraRsAccPortP'

    #Get all the switch profiles
    switchProfiles = md.query(q)

    nodes = {}
    print "Switch profile analysis"
    for switchProfile in switchProfiles:

        # Extract the leafs and portProfiels objects attached to the current Switch Profile and save them into a list.
        leafs = []
        portProfiles = []
        print '\t', switchProfile.name, 'Analysed'
        for child in switchProfile.children:
            node_exist = False
            #First I need to extract the leaf and port (within a switch Profile) as I need to process the swirtches first.
            if type(child) is cobra.model.infra.LeafS:
                leafs.append(child)
                #If a switch profiles is not mapped to a leaf selector then the node does not exists.
                node_exist = True

            if type(child) is cobra.model.infra.RsAccPortP:
                portProfiles.append(child)

        # If there are nodes in the SwitchProfle add them to the nodes dictionary.
        if node_exist:
            for leaf in leafs:
                for leaf_child in leaf.children:
                        # print type(sub)
                    if type(leaf_child) is cobra.model.infra.NodeBlk:
                        node_blk = leaf_child
                        # print '\t', leaf_child.from_
                        # print '\t', leaf_child.to_
                        # print '\t range', range(int(leaf_child.from_), int(leaf_child.to_)+1)
                        for node_id in range(int(node_blk.from_), int(node_blk.to_)+1):
                            if node_id not in nodes:
                                nodes[node_id] = Node(node_id)

        # If there are NO nodes in the SwitchProfle then I create a dummy node to hold possible orphan port selectors
        if not node_exist:
            if NAN not in nodes:
                nodes[NAN] = Node(NAN)

        # Now I analyse all the portProfiles
        for portProfile in portProfiles:
            # Get the port profile parent (port selector)
            q2 = cobra.mit.request.DnQuery(portProfile.tDn)
            q2.subtree = 'full'
            q2.subtreeClassFilter = 'infraHPortS,infraPortBlk'
            portsSel = md.query(q2)
            for portSel in portsSel:
                for portSel_child in portSel.children:
                    # print '\t' ,child2.name
                    for portSel_child_child in portSel_child.children:
                        # print '\t\tModule', portSel_child_child.fromCard, '-', portSel_child_child.toCard
                        # print '\t\tport' , portSel_child_child.fromPort, '-', portSel_child_child.toPort
                        if type(portSel_child_child) is cobra.model.infra.PortBlk:
                            port_blk = portSel_child_child
                            for module_id in range(int(port_blk.fromCard), int(port_blk.toCard)+1):
                                for port_id in range(int(port_blk.fromPort), int(port_blk.toPort)+1):
                                    if node_exist:
                                        for node_id in range(int(node_blk.from_), int(node_blk.to_)+1): #current_nodes:
                                            # print 'debug', node_id
                                            nodes[node_id].add_port(str(module_id) + '/' + str(port_id), switchProfile.name)
                                    else:
                                        nodes[NAN].add_port(str(module_id) + '/' + str(port_id), switchProfile.name)

    return nodes


########
# Main #
########

# Set up arg parse

parser = argparse.ArgumentParser()
parser.add_argument("-n", nargs = '*', help='List of Node ID')
# parser.add_argument("-p", nargs = '*', help='List of Port x/y or x/y-z')
args = parser.parse_args()

nodes = get_nodes_port_data()

output = PrettyTable(['Node','Ports'])
output.align = 'l'
output.max_width = 150


for key, node in nodes.items():
    port_string = ''
    for port in node.get_sorted_ports():
        port_string = port + ' ' + port_string
    output.add_row([node.id, port_string])

print output

if NAN in nodes:

    print "\nWARNING These switch profiles are selecting port(s) but not mapping them to a Switch Selector!!!!"
    output = PrettyTable(['Switch Profile','Ports'])
    output.align = 'l'
    output.max_width = 150


    for switchProfile, ports in nodes[NAN].get_port_per_sw_pfl().items():
        port_string = ''
        for port in ports:
            port_string = port + ' ' + port_string
        output.add_row([switchProfile, port_string])
    print output


