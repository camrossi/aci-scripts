#vnsAbsConnection --> SG Connector class
#vnsEPgDef --> Shadow EPG of the SG, here you can get the PC TAG!
#
#vnsFuncConnInst,vnsRtEPgDefToConn,vnsEPgDe
#
#
#vnsGraphInst --> vnsNodeInst --> vnsLegVNode --> vnsEPgDef (pcTAG)
# 
#vnsGraphInst --> vnsNodeInst --> vnsRsNodeInstToLDevCtx -->  
# vnsLDevVip --> vnsRtNodeToLDev

import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
from cobra.internal.codec.xmlcodec import toXMLStr
import yaml
from pprint import pprint

class Node():
    def __init__(self, Name, Node_ID):
       pass
class ServiceGraph():
    def __init__(self, ctrctName, filtName, md):
        self.ctrctName = unicode(ctrctName)
        self.filtName = unicode(filtName)
        self.consEPG = []
        self.provEPG = []
        self.md = md
        self.nodes = {}
        # Get Contract/Subject Graph
        q = cobra.mit.request.ClassQuery('vnsGraphInst')
        q.subtree = 'full'
        q.subtreeClassFilter = 'vnsAbsGraph,vnsAbsTermNodeProv,vnsAbsTermNodeCon,vnsAbsNode,vnsRsMConnAtt,vnsAbsDevCfg,vnsAbsFolder,vnsRsScopeToTerm,vnsAbsGrpCfg,vnsAbsParam,vnsAbsFuncCfg,vnsRsNodeToMFunc,vnsRsNodeToLDev,vnsAbsConnection,vnsRsAbsConnectionConns,vnsAbsFuncConn,vnsAbsTermConn,vnsRsAbsCopyConnection,vnsRsNodeToAbsFuncProf'
        #q.propFilter = 'wcard(vzBrCP.dn, "{}")'.format(ctrctName)
        #q.subtreePropFilter = 'wcard(vzSubj.dn, "{}")'.format(filtName)
        contract =  md.query(q)
        # Get Consumer EPG
        for epg in contract[0].rtfvCons:
            self.consEPG.append(epg.tDn)

        # Get Provider EPG
        for epg in contract[0].rtfvProv:
            self.provEPG.append(epg.tDn)

        for sub in contract[0].subj:
            for rsSubjGraphAtt in sub.rsSubjGraphAtt:
                print rsSubjGraphAtt.tDn
        
        
        
        
        print("ConsEPG {}, Provider EPG {}").format(self.consEPG, self.provEPG)
# open yaml files with the credentials
f = open('credentials.yaml', 'r')
credentials = yaml.load(f)
f.close()
# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(credentials['host'], credentials['user'], credentials['pass'], secure=False, timeout=180)
md = cobra.mit.access.MoDirectory(ls)
md.login()

sg = ServiceGraph('FW_IPS_LB', 'Subject', md)

#
#        #load all L4-7 Devices and the pointer to the vnsAbsNode
#        q = cobra.mit.request.ClassQuery('vnsLDevVip')
#        q.subtree = 'children'
#        q.subtreeClassFilter = 'vnsRtNodeToLDev'
#
#        devs = md.query(q)
#
#:Wq

#
#vnsAbsNode = {}
#
#for dev in devs:
#    for vnsRtNodeToLDev in dev.rtnodeToLDev:
#        vnsAbsNode[str(vnsRtNodeToLDev.tDn)] = dev.name
#
#contract_name = "brc-FW_IPS_LB"
#q = cobra.mit.request.ClassQuery('vnsGraphInst')
#q.propFilter = 'wcard(vnsGraphInst.ctrctDn, "{}")'.format(contract_name)
#q.subtree = 'full'
#q.subtreeClassFilter = 'vnsNodeInst,vnsLegVNode,vnsEPgDef,vnsRsNodeInstMeta'
#
#GraphInstances = md.query(q)
#for graph in GraphInstances:
#    for NodeInst in graph.NodeInst:
#        for vnsRsNodeInstMeta in NodeInst.rsNodeInstMeta:
#            print vnsAbsNode[vnsRsNodeInstMeta.tDn]
#        for LegVNode in NodeInst.LegVNode:
#            for EPgDef in LegVNode.EPgDef:
#                print EPgDef.pcTag
#
####
