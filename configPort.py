from cobra.model.fv import Ap, AEPg, RsBd, RsCustQosPol, RsAEPgMonPol, RsDomAtt, RsNodeAtt, RsPathAtt

from apicPython.createMo import *
from apicPython import createLinkLevelPolicy
from apicPython import createCdpInterfacePolicy
from apicPython import createLldpInterfacePolicy
from apicPython import createLacpPolicy
import configureInterfacePcAndVpc
import createvPcInterfacePolicyGroup
from apicPython import createAccessPortPolicyGroup
from apicPython import createPcInterfacePolicyGroup
from apicPython import createAttachableAccessEntityprofile
import warnings

warnings.filterwarnings("ignore")


DEFAULT_QOS = 'unspecified'
DEFAULT_BRIDGE_DOMAIN = 'None'
DEFAULT_CUSTOM_QOS = 'None'
DEFAULT_POLICY = 'None'
DEFAULT_IMMEDIACY = 'lazy'
DEFAULT_MODE = 'regular'

IMMEDIACY_CHOICES = ['immediate', 'lazy']
QOS_CHOICES = ['level1', 'level2', 'level3', 'unspecified']
MODE_CHOICES = ['regular', 'native', 'untagged']


def input_epg_name(msg='\nPlease input Application EPG info:'):
    print msg
    return input_raw_input("EPG Name", required=True)


def input_domain_profile(msg='\nAssociating Domain Profile (VMs or bare metals):'):
    print msg
    return input_raw_input("domain_profile", required=True)


def input_domain_profile_optional_args(*args):
    args = {}
    args['deployment_immediacy'] = input_options('Deploy Immediacy', DEFAULT_IMMEDIACY, IMMEDIACY_CHOICES)
    args['resolution_immediacy'] = input_options('Resolution Immediacy', DEFAULT_IMMEDIACY, IMMEDIACY_CHOICES)
    return args


def input_leaf(msg='\nplease specify static links leaves'):
    print msg
    args = {'node_id': input_raw_input('Node ID', default='None')}
    if is_valid_key(args, 'node_id', ban=['None']):
        args['encap'] = input_raw_input('Encap', required=True)
        args['deployment_immediacy'] = input_options('Deploy Immediacy', DEFAULT_IMMEDIACY, IMMEDIACY_CHOICES)
        args['mode'] = input_options('Mode', DEFAULT_MODE, MODE_CHOICES)
    return args


def input_path(msg='\nplease specify static links paths'):
    print msg
    # args = {'node_id': input_raw_input('Node ID', default='None'),
    #         'eth': input_raw_input('Eth number', default='None')}
    # if is_valid_key(args, 'node_id', ban=['None']) and is_valid_key(args, 'eth', ban=['None']):
    args = {'encap' : input_raw_input('Encap', required=True),
            'deployment_immediacy': input_options('Deploy Immediacy', DEFAULT_IMMEDIACY, IMMEDIACY_CHOICES),
            'mode': input_options('Mode', DEFAULT_MODE, MODE_CHOICES)}
    return args


def input_optional_args(*key):
    args = {'bridge_domain': input_raw_input('Bridge Domain', default=DEFAULT_BRIDGE_DOMAIN),
            'prio': input_options('Prio(QoS Class)', DEFAULT_QOS, QOS_CHOICES),
            'custom_qos': input_raw_input('Custom QoS', default=DEFAULT_CUSTOM_QOS),
            'monitoring': input_raw_input("Monitoring Policy", default=DEFAULT_POLICY),
            # 'associated_domain_profile': read_add_mos_args(
            #     add_mos('Add an Associated Domain Profile', input_domain_profile, input_domain_profile_optional_args),
            #     get_opt_args=True),
             'statically_link': input_yes_no('Apply Statically Link with Leaves/Paths', default='False')
    }
    if args['statically_link']:
    #     # I need only the path not the leaf
    #     # args['leaf'] = input_leaf()
         args['path'] = input_path()
    return args

def createPortPolicyGroup(mo, interface_policy_group,interface_type, **args):
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    if interface_type == 'individual':
        createAccessPortPolicyGroup.create_access_port_port_policy_group(mo, interface_policy_group, optional_args= args)

    elif interface_type in ['pc', 'PC']:
        createPcInterfacePolicyGroup.create_pc_interface_policy_group(mo, interface_policy_group, optional_args= args)
    elif interface_type in ['VPC', 'vpc']:
        createvPcInterfacePolicyGroup.create_vpc_interface_policy_group(mo, interface_policy_group, optional_args= args)
    else:
        print 'Invalid interface type. Option of interface type is "individual", "pc" or, "vpc".'
        sys.exit()


def create_application_epg(fv_ap, epg,interface_type, **args):
    """Create a Application. A set of requirements for the application-level EPG instance. The policy regulates connectivity and visibility among the end points within the scope of the policy. """
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    fv_aepg = AEPg(fv_ap, epg,
                   prio=get_value(args, 'prio', 'unspecified').lower())


    # Provide bridge_domain to the EPG.
    if is_valid_key(args, 'bridge_domain'):
        fv_rsbd = RsBd(fv_aepg, tnFvBDName=args['bridge_domain'])

    if is_valid_key(args, 'custom_qos'):
        fv_rscustqospol = RsCustQosPol(fv_aepg, tnQosCustomPolName=args['custom_qos'])

    if is_valid_key(args, 'monitoring'):
        fv_rsaepgmonpol = RsAEPgMonPol(fv_aepg, tnMonEPGPolName=args['monitoring'])

    if is_valid_key(args, 'associated_domain_profile'):
        for profile in args['associated_domain_profile']:
            fv_rsdomatt = RsDomAtt(fv_aepg, 'uni/phys-' + profile['domain_profile'],
                                   instrImedcy=get_value(profile, 'deployment_immediacy', DEFAULT_IMMEDIACY),
                                   resImedcy=get_value(profile, 'resolution_immediacy', DEFAULT_IMMEDIACY))

    if is_valid_key(args, 'statically_link') and args['statically_link']:
        if is_valid_key(args, 'leaf') and is_valid_key(args['leaf'], 'node_id', ban=['None']):
            fv_rsnodeatt = RsNodeAtt(fv_aepg, 'topology/pod-1/node-' + str(args['leaf']['node_id']),
                                     encap=args['leaf']['encap'],
                                     mode=get_value(args['leaf'], 'mode', DEFAULT_MODE),
                                     instrImedcy=get_value(args['leaf'], 'deployment_immediacy', DEFAULT_IMMEDIACY))

        if is_valid_key(args, 'path') and is_valid_key(args['path'], 'node_id', ban=['None']):
            if interface_type == "individual":
                pathep = '/pathep-[eth'
                paths = 'paths-'
            elif interface_type in ['pc','PC']:
                pathep = '/pathep-['
                paths = 'paths-'
            else:
                pathep = '/pathep-['
                paths = 'protpaths-'
            fv_rsnodeatt = RsPathAtt(fv_aepg, 'topology/pod-1/' + paths + str(args['path']['node_id']) + pathep +
                                     args['path']['eth'] + ']',
                                     encap=args['path']['encap'],
                                     mode=get_value(args['path'], 'mode', DEFAULT_MODE),
                                     instrImedcy=get_value(args['path'], 'deployment_immediacy', DEFAULT_IMMEDIACY))

    return fv_aepg


class ConfigurePort(CreateMo):
    def __init__(self):
        self.description = 'Create a Application EPG. A set of requirements for the application-level EPG instance. The policy regulates connectivity and visibility among the end points within the scope of the policy. '
        self.tenant_required = True
        self.tenant = 'mgmt'
        self.epg = None
        self.link_level_policy = {}
        self.cdp_interface_policy = {}
        self.lldp_interface_policy = {}
        self.lacp_policy = {}
        self.switch_profile = None
        self.interface_type = None
        self.interface_selector = None
        self.interface_policy_group = None
        self.interface_ports = []
        self.switches = []
        self.entity_profile = None
        self.switch_selector = None
        self.interface_selector_profile = None

        super(ConfigurePort, self).__init__()

    def set_cli_mode(self):
        super(ConfigurePort, self).set_cli_mode()
        self.parser_cli.add_argument('application', help='Application Name')
        self.parser_cli.add_argument('epg', help='Application EPG Name')
        self.parser_cli.add_argument('-Q', '--QoS_class', dest='prio', default=DEFAULT_QOS, choices=QOS_CHOICES,
                                     help='The priority level of a sub application running behind an endpoint group.')
        self.parser_cli.add_argument('-q', '--custom_qos',
                                     help='A relation to a custom QoS policy that enables different levels of service to be assigned to network traffic, including specifications for the Differentiated Services Code Point (DSCP) value(s) and the 802.1p Dot1p priority. This is an internal object.')
        self.parser_cli.add_argument('-b', '--bridge_domain',
                                     help='A relation to the bridge domain associated to this endpoint group.')
        self.parser_cli.add_argument('-m', '--monitoring', default=DEFAULT_POLICY, help='The monitoring policy name.')
        self.parser_cli.add_argument('-s', '--statically_link', action='store_const', const=True, default=False,
                                     help='Statically link with Leaves/Paths')
        self.parser_cli.add_argument('-l', '--leaf', nargs=4,
                                     help='The static association with an access group, which is a bundled or unbundled group of ports. Arguments are: Node ID, Encap, Deployment Immediacy and Mode.')
        self.parser_cli.add_argument('-p', '--path', nargs=5,
                                     help='A static association with a path. Arguments are: Node ID, eth number, Encap, Deployment Immediacy and Mode.')

    def run_wizard_mode(self):
        self.args = {
             'host': "",
             'user': "",
             'password': ""
        }
        if self.tenant_required:
            self.args['tenant'] = input_raw_input("Tenant Name", required=True)
            self.tenant = self.args['tenant']

        self.host = ""
        self.user = ""
        self.password = ""
        self.apic_login()
        self.wizard_mode_input_args()
        self.read_key_args()
        self.read_opt_args()


    def wizard_mode_input_args(self):

        self.switches, self.switch_profile, self.switch_selector,self.interface_selector_profile, self.interface_type, self.interface_ports, self.interface_policy_group = configureInterfacePcAndVpc.input_key_args()
        self.link_level_policy['name'] = createLinkLevelPolicy.input_key_args()
        self.cdp_interface_policy['name'] = createCdpInterfacePolicy.input_key_args()
        self.lldp_interface_policy['name'] = createLldpInterfacePolicy.input_key_args()
        self.lacp_policy['name'] = createLacpPolicy.input_key_args()
        self.entity_profile = createAttachableAccessEntityprofile.input_key_args()

        self.args['application'] = self.input_application_name()
        self.args['epg'] = input_epg_name()
       # if not self.delete:
        #    self.args['optional_args'] = input_optional_args()
            # if is_valid_key(self.args['optional_args'], 'associated_domain_profile'):
            #     associated_domain_profile = []
            #     for i in range(len(self.args['optional_args']['associated_domain_profile'][0])):
            #         associated_domain_profile.append(dict(
            #             {'domain_profile': self.args['optional_args']['associated_domain_profile'][0][i]}.items() +
            #             self.args['optional_args']['associated_domain_profile'][1][i].items()))
            #     self.args['optional_args']['associated_domain_profile'] = associated_domain_profile

        if len(self.switches) == 2:
            self.args['node_id'] = self.switches[0] + '-' + self.switches[1]
            self.args['eth'] = self.interface_selector_profile
        elif len(self.switches) == 1:
            self.args['node_id'] = self.switches[0]
            self.args['eth'] = self.interface_ports

    def run_yaml_mode(self):

        f = open('credentials.yaml', 'r')
        credentials = yaml.load(f)
        f.close()
        f = open(self.args['yaml_file'], 'r')
        self.args = yaml.load(f)
        f.close()

        self.host = credentials['host']
        self.user = credentials['user']
        self.password = credentials['pass']
        self.application = self.args['application']
        # self.epg = self.args['epg']
        self.tenant = self.args['tenant']
        self.switches = self.args["switches"]
        self.interface_type = self.args["interface_type"]
        self.interface_policy_group = self.args["interface_policy_group"]
        self.interface_selector = self.args["interface_selector"]
        self.link_level_policy = self.args["link_level_policy"]
        self.cdp_interface_policy = self.args["cdp_interface_policy"]
        self.lldp_interface_policy = self.args["lldp_interface_policy"]
        self.lacp_policy = self.args["lacp_policy"]
        self.entity_profile = self.args["attachable_entity_profile"]
        self.optional_args = self.args["optional_args"]
        if not self.delete:
            self.args['optional_args'] = self.args['optional_args']
            if is_valid_key(self.args['optional_args'], 'associated_domain_profile'):
                associated_domain_profile = []
                for i in range(len(self.args['optional_args']['associated_domain_profile'][0])):
                    associated_domain_profile.append(dict(
                        {'domain_profile': self.args['optional_args']['associated_domain_profile'][0][i]}.items() +
                        self.args['optional_args']['associated_domain_profile'][1][i].items()))
                self.args['optional_args']['associated_domain_profile'] = associated_domain_profile

        #TfNSW Hard Coding names
        if len(self.switches) == 2:
            self.switch_profile = "Leaves" + str(self.switches[0]) +"n" +  str(self.switches[1]) + '-SwiPfl'
            self.switch_selector = "Leaves" + str(self.switches[0]) +"n" +  str(self.switches[1]) + '-SwiSel'
            self.interface_selector_profile = "Leaves" + str(self.switches[0]) +"n" +  str(self.switches[1]) + '-IntSelPfl'
        elif len(self.switches) == 1:
            self.switch_profile = "Leaf" + str(self.switches[0]) + '-SwiPfl'
            self.switch_selector = "Leaf" + str(self.switches[0]) + '-SwiSel'
            self.interface_selector_profile = "Leaf" + str(self.switches[0]) + '-IntSelPfl'
        if self.interface_type in ['individual']:
            self.optional_args['path']['node_id'] = self.switches[0]
            self.optional_args['path']['eth'] = self.interface_selector[self.interface_selector.keys()[0]][0] #UGLY CHECK ME
        elif self.interface_type in ['pc', 'PC']:
            self.optional_args['path']['node_id'] = self.switches[0]
            self.optional_args['path']['eth'] = self.interface_policy_group
        elif self.interface_type in ['VPC', 'vpc','pc', 'PC']:
            self.optional_args['path']['node_id'] = str(self.switches[0]) +'-' + str(self.switches[1])
            self.optional_args['path']['eth'] = self.interface_policy_group

        self.apic_login()

    def delete_mo(self):
        self.check_if_mo_exist('uni/tn-' + self.tenant + '/ap-' + self.application + '/epg-', self.epg, AEPg,
                               description='Application EPG')
        super(ConfigurePort, self).delete_mo()


    def main_function(self):

        self.look_up_mo('uni/infra/funcprof/', '')

        createPortPolicyGroup(self.mo, self.interface_policy_group,self.interface_type,optional_args={'link_level': self.link_level_policy['name'],
                                                                                  'cdp': self.cdp_interface_policy['name'],
                                                                                  'lldp': self.lldp_interface_policy['name'],
                                                                                  'lacp': self.lacp_policy['name'],
                                                                                  'entity_profile': self.entity_profile})



        self.commit_change()
        # configure PC
        self.look_up_mo('uni/infra', '')
        configureInterfacePcAndVpc.configure_interface_pc_and_vpc(self.mo, self.switch_profile, self.switch_selector, self.switches,
                                                                  self.interface_type,self.interface_selector_profile,
                                                                  self.interface_selector, self.interface_policy_group)
        self.commit_change()

if __name__ == '__main__':
    mo = ConfigurePort()