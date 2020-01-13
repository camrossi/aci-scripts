__author__ = 'cpaggen'
__author__ = 'ddastoli'

# connects to APIC and returns nodes + ports where user-specified VLAN is found
# version 1.1a
# to do: 
#   - given an interface, list AAEPs and domains and VLANs this interfaces points to
#
# June 2018 - PoC-level code; perfoms ROs only - safe to use anywhere
#

import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fvns
import cobra.mit.naming
import re
import sys
import requests
import logging
logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings()


def setLogLevel(logLevel):
    logging.basicConfig(stream=sys.stderr, level=logLevel.upper())
    logger.info('Logging level set to {}'.format(logLevel))
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

def apicLogin(ip, username, password):
    # log into an APIC and create a directory object
    url = "https://" + ip
    logger.info('Logging into APIC ...')
    ls = cobra.mit.session.LoginSession(url, username, password, secure=False, timeout=180)
    moDir = cobra.mit.access.MoDirectory(ls)
    try:
        moDir.login()
    except:
        logger.critical("Login error (wrong username or password?)")
        sys.exit(1)
    return moDir

def findVlan(vlanId, moDir):
    logger.info("Processing all VLANs ...")
    vlanBitMap = {}
    vlanPools = moDir.lookupByClass('fvnsVlanInstP')
    for pool in vlanPools:
        #print pool.name + ' is ' + pool.allocMode
        VlanInstPChildren = moDir.lookupByClass(pool.children, pool.dn)
        # per the object model, children are fvnsEncapBlk, RtVlanNs and VlanInstP
        for child in VlanInstPChildren:
            if 'EncapBlk' in child.dn.meta.moClassName:
                # extract VLANs in each EncapBlk
                # one of the naming props is called "from" which is a reserved keyword, use __dict__ workaround instead
                vlanFromTo = 'from {} to {}'.format(str(child.__dict__['from']), str(child.to))
                # print '\t --> ' + vlanFromTo
                p = re.compile('\d+')
                vlanList = p.findall(vlanFromTo)
                # expand VLAN ranges
                vlanRange = range(int(vlanList[0]),int(vlanList[1])+1)
                # build a dictionary keyed on VLAN number. If VLAN is found in a pool, add pool's dn(s) as value(s)
                for vlan in vlanRange:
                    try:
                        vlanBitMap[vlan]
                    except KeyError:
                        vlanBitMap[vlan] = str(child.parentDn)
                    else:
                        vlanBitMap[vlan] += (" *and* " + str(child.parentDn))
    logger.info("\tVLAN bit map built with {} hits".format(len(vlanBitMap)))
    try:
        vlanBitMap[vlanId]
    except KeyError:
        logger.critical("VLAN {} does not exist on this fabric".format(vlanId))
        sys.exit(1)
    else:
        logger.info("\t--> the following VLAN pool(s) contain VLAN {}".format(vlanId))
        logger.info("\t\t{}".format(vlanBitMap[vlanId]))
        return vlanBitMap


def findDomain(vlanBitMap, VLAN, moDir):
    # find Domains (phys, VMM, L2 and L3) where the VLAN pool is present
    listOfDomains = []
    listOfOrphanDomains = []
    physDoms = moDir.lookupByClass('physDomP')
    l2Doms = moDir.lookupByClass('l2extDomP')
    l3Doms = moDir.lookupByClass('l3extDomP')
    VMMDoms = moDir.lookupByClass('vmmDomP')
    # built list of all pools (DNs) this VLAN is a member of
    vlanPools = vlanBitMap[VLAN].split(" *and* ")
    domsToProcess = [physDoms, l2Doms, l3Doms, VMMDoms]
    logger.info("Processing domains ...")
    for doms in domsToProcess:
        for dom in doms:
            logger.debug("\t --> processing domain {}".format(dom.dn))
            dn = str(dom.dn) + '/rsvlanNs'
            rsVlanNs = moDir.lookupByDn(dn)
            # check whether domain has a relation to a pool our VLAN is a member of
            # a domain can have {0,1} relation to a VLAN pool
            try:
                for vlanPool in vlanPools:
                    if str(vlanPool) == str(rsVlanNs.tDn):
                        listOfDomains.append(dom)
                        logger.debug("\t\t\tVLAN {} in pool {} found in this domain".format(VLAN,vlanPool))
            except AttributeError:
                listOfOrphanDomains.append(dom)
                logger.debug("\t\t\tthis domain is not bound to any VLAN pool, skipping ...")

    logger.debug("\t --> done with domains.")
    if listOfDomains:
        logger.info("\tVLAN {} is present in the following domains:".format(VLAN))
        for domain in listOfDomains:
            logger.info('\t\t{}'.format(domain.dn))
    else:
        logger.info("\t\tVLAN {} exists but its pool is not bound to any domain".format(VLAN))
        sys.exit(1)
    return listOfDomains,listOfOrphanDomains

def findAEP(DomainsWhereVLANis, moDir):
    # find AEPs that have a relation to domain(s) our VLAN is a member of
    # if an AEP has no relation to such a domain, there can be no interface where that VLAN exists
    listOfAEP = []
    logger.info("Processing AEPs ...")
    AEPs = moDir.lookupByClass('infraAttEntityP')
    for AEP in AEPs:
        logger.debug("\t --> found AEP {}".format(AEP.dn))
        for domain in DomainsWhereVLANis:
            dn = str(AEP.dn) + '/rsdomP-['+str(domain.dn)+']'
            rsDomP = moDir.lookupByDn(dn)
            try:
                if domain.dn == rsDomP.tDn:
                    if AEP not in listOfAEP:
                        listOfAEP.append(AEP)
                        logger.debug("\t\t\tdomain {} is a tDn of this AEP".format(str(domain.dn)))
            except AttributeError:
                logger.debug("\t\t\tthis AAEP has no tDn relation with {}".format(dn))
    logger.info("\t --> AEP(s) that have a relation to the domain(s) where VLAN is present:")
    for foundAEP in listOfAEP:
        logger.info('\t\t{}'.format(foundAEP.dn))
    return listOfAEP

def findAccPortGrp(AEPs, moDir):
    # find interface policy groups that bind to the AAEP we are interested in
    listPolicyGrp = []
    ifpolgrp = moDir.lookupByClass('infraAccPortGrp')
    portChannelsGrps = moDir.lookupByClass('infraAccBndlGrp')
    logger.info("Processing Interface Policy Groups ...")
    logger.debug("\t --> found {} Interface Policy Groups".format(len(ifpolgrp)))
    # TODO: write small function to avoid code repetition below
    for policy in ifpolgrp:
        dn = str(policy.dn) + '/rsattEntP'
        # child of infraAccPortGrp 'infraRsAttEntP' points to AEP
        rsattenp = moDir.lookupByDn(dn)
        for AEP in AEPs:
            logger.debug("\t --> searching for reference to {}".format(AEP.dn))
            try:
                if rsattenp.tDn == AEP.dn:
                    logger.debug("\t\t{} is bound to {}".format(dn,str(rsattenp.tDn)))
                    listPolicyGrp.append(policy)
            except AttributeError:
                logger.debug("\t\tpolicy group {} is not bound to this AEP".format(dn))
    for bundlePol in portChannelsGrps:
        dn = str(bundlePol.dn) + '/rsattEntP'
        rsattenp = moDir.lookupByDn(dn)
        for AEP in AEPs:
            logger.debug("\t --> processing port-channels")
            try:
               if rsattenp.tDn == AEP.dn:
                   logger.debug("\t\t is bound to {}".format(dn,str(rsattenp.tDn)))
                   listPolicyGrp.append(bundlePol)
            except AttributeError:
                logger.debug("\t\tport-channel policy group {} is not bound to this AEP".format(dn))
    logger.info("\t --> interface policy groups(s) that have a relation to the AAEP where VLAN is present:")
    for foundPol in listPolicyGrp:
        logger.info('\t\t{}'.format(foundPol.dn))
    return listPolicyGrp

def findPorts(AccPortGrp,VLAN,moDir):
    # find relationship between interface policy group(s) and interface selector(s)
    listHPortS = []
    portBitMap = {}
    logger.info("Processing interfaces ...")
    # fetch all interface selectors
    hPortS = moDir.lookupByClass('infraHPortS')
    for hPort in hPortS:
        dn = str(hPort.dn) + '/rsaccBaseGrp'
        rsacc = moDir.lookupByDn(dn)
        for elem in AccPortGrp:
            if rsacc.tDn == elem.dn:
                if hPort not in listHPortS:
                    logger.debug('\t --> adding port selector {} to list '.format(str(hPort.dn)))
                    listHPortS.append(hPort)
    logger.debug("\t --> querying system for if_profiles, leafs, node blocks, nodes and port blocks ...")
    portProf = moDir.lookupByClass('infraAccPortP')
    vpcPortProf = moDir.lookupByClass('infraAccBndlGrp')
    leafs = moDir.lookupByClass('infraLeafS')
    nBlocks = moDir.lookupByClass('infraNodeBlk')
    nodeBlk = []
    for n in nBlocks:
        if 'mgmtnodegrp' not in str(n.dn):
            nodeBlk.append(n)
    nodeProf = moDir.lookupByClass('infraNodeP')
    portblk = moDir.lookupByClass('infraPortBlk')
    logger.debug('''
         \t\t  Looking for Interface Profiles ...
         \t\t\t --> found {} Interface Profiles
         \t\t  Looking for Leafs ...
         \t\t\t --> found {} Leafs
         \t\t  Looking for Node Blocks ...
         \t\t\t --> found {} Node Blocks
         \t\t  Looking for Nodes ...
         \t\t\t --> found {} Nodes
         \t\t  Looking for all port blocks ...
         \t\t\t --> found {} Port Blocks
         '''.format(len(portProf),len(leafs),len(nodeBlk),len(nodeProf),len(portblk)))

    for nBlock in nodeBlk:
        from_ = nBlock.from_
        to_ = nBlock.to_
        portBitMap[from_]=[]
        portBitMap[to_]=[]

    logger.debug("Results ...")
    logger.debug("VLAN {} is present on the following ports:".format(VLAN))
    for prof in nodeProf:
        for elem in portProf:
            dn = str(prof.dn) + '/rsaccPortP-[' + str(elem.dn) + ']'
            rsAccPortP = moDir.lookupByDn(dn)

            for ifSelector in listHPortS:
                try:
                    if str(ifSelector.dn)[0:str(ifSelector.dn).find('/hports')] == rsAccPortP.tDn:
                        for leaf in leafs:
                            str_node = str(rsAccPortP.dn)[0:str(rsAccPortP.dn).find('/rsaccPortP')]
                            if str_node in str(leaf.dn):
                                for nBlock in nodeBlk:
                                    if str(leaf.dn) in str(nBlock.dn):
                                        # build a dictionary keyed on VLAN number. If VLAN is found in a pool, add pool's dn(s) as value(s)
                                        logger.debug("\t\t\t" + str(leaf.dn) + ' --> ' + nBlock.from_ + ' to ' + nBlock.to_)
                                        for block in portblk:
                                            if str(ifSelector.dn) in str(block.dn):
                                                interfaces = block.fromCard + '/' + block.fromPort + ' to ' + block.toCard + '/' + block.toPort
                                                # avoid creating duplicate entries per leaf
                                                if interfaces not in portBitMap[nBlock.from_]:
                                                    portBitMap[nBlock.from_].append(interfaces)
                                                    logger.debug("\t\t\tifSelector {} --> {}".format(str(ifSelector.dn),interfaces))
                except AttributeError:
                    logger.debug("\t\t{} is not bound to any interface policy group!".format(dn))
    return portBitMap


def main(ip, username, password, VLAN, logLevel):
    setLogLevel(logLevel)
    moDir = apicLogin(ip, username, password)
    vlanBitMap = findVlan(VLAN, moDir)
    domains,orphans = findDomain(vlanBitMap,VLAN,moDir)
    AEP = findAEP(domains, moDir)
    AccPortGrp = findAccPortGrp(AEP, moDir)
    Ports = findPorts(AccPortGrp,VLAN,moDir)
    print "\nVLAN {} is configured on the following nodes and ports:".format(VLAN)
    for k,v in Ports.items():
        print k,v

if __name__ == '__main__':
    print "This code logs onto a given APIC and looks for all ports where a specified VLAN is configured"
    if len(sys.argv) != 6:
        print "No parameters or insufficient parameters provided; going in interactive mode\n"
        ip = raw_input("IP: ")
        username = raw_input("username: ")
        password = raw_input("password: ")
        vlan = int(raw_input("VLAN: "))
        logLevel = raw_input("Logging level (info or debug): ")
    else:
        ip, username, password, vlan, logLevel = sys.argv[1:]

    main(ip,username,password,int(vlan),logLevel)
