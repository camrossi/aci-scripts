__author__ = 'camrossi'

#
# Written by Camillo Rossi @ Cisco System February 2015
#!/usr/bin/env python
# list of packages that should be imported for this code to work

import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import cobra.model.vns
import cobra.mit.naming


class NetScaler():
    def __init__(self, ctrctName, graphName, nodeName, fvAEPg, topMo, md):
        self.ctrctName = unicode(ctrctName)
        self.graphName = unicode(graphName)
        self.nodeName = unicode(nodeName)
        self.fvAEPg = fvAEPg
        self.topMo = topMo
        self.md = md

    def create_l4_7_device():
        pass

    def add_ip(self, name, ip, mask):

        network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'Network', cardinality=u'unspecified',locked=u'no',name=u'network',
                                                    scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        nsipfolder = cobra.model.vns.FolderInst(network, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                key=u'nsip', cardinality=u'unspecified', locked=u'no',
                                                name=unicode(name),
                                                scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'ipaddress', cardinality=u'unspecified',
                                  locked=u'no', name=u'ipaddress', value=unicode(ip), validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'hostroute', cardinality=u'unspecified',
                                  locked=u'no',
                                  name=u'hostroute', value=u'DISABLED', validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'netmask', cardinality=u'unspecified', locked=u'no',
                                  name=u'netmask', value=unicode(mask), validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'dynamicrouting', cardinality=u'unspecified',
                                  locked=u'no', name=u'dynamicrouting', value=u'DISABLED', validation=u'')


        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'type', cardinality=u'unspecified', locked=u'no',
                                  name=u'type', value=u'SNIP', validation=u'')


        internal_network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                      key=u'internal_network', cardinality=u'unspecified', locked=u'no',
                                                      name=u'internal_network-' + unicode(name), scopedBy=u'epg', devCtxLbl=u'',
                                                      nodeNameOrLbl=self.nodeName)
        cobra.model.vns.CfgRelInst(internal_network, locked=u'no', name=u'internal_network_key', key=u'internal_network_key',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=u'network/' + unicode(name))


        self.__commit()

    def remove_ip(self, name):

        network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'Network', cardinality=u'unspecified',locked=u'no',name=u'network',
                                                    scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        nsipfolder = cobra.model.vns.FolderInst(network, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                key=u'nsip', cardinality=u'unspecified', locked=u'no',
                                                name=unicode(name),
                                                scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)


        internal_network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                      key=u'internal_network', cardinality=u'unspecified', locked=u'no',
                                                      name=u'internal_network-' + unicode(name), scopedBy=u'epg', devCtxLbl=u'',
                                                      nodeNameOrLbl=self.nodeName)
        nsipfolder.delete()
        internal_network.delete()

        self.__commit()

    def add_route(self, name, net, mask, gw):

        name = unicode(name)
        net = unicode(net)
        mask = unicode(mask)
        gw = unicode(gw)

        network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'Network', cardinality=u'unspecified',locked=u'no',name=u'network',
                                                    scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        route = cobra.model.vns.FolderInst(network, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                            key=u'route', cardinality=u'unspecified', locked=u'no', name=name,
                                            scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)


        cobra.model.vns.ParamInst(route, key=u'netmask', cardinality=u'unspecified', locked=u'no', name=u'netmask',
                                  value=mask)
        cobra.model.vns.ParamInst(route, key=u'network', cardinality=u'unspecified', locked=u'no', name=u'network',
                                  value=net)
        cobra.model.vns.ParamInst(route, key=u'gateway', cardinality=u'unspecified', locked=u'no', name=u'gateway',
                                  value=gw)

        self.__commit()

    def remove_route(self, name):

        name = unicode(name)

        network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'Network', cardinality=u'unspecified',locked=u'no',name=u'network',
                                                    scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        route = cobra.model.vns.FolderInst(network, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                            key=u'route', cardinality=u'unspecified', locked=u'no', name=name,
                                            scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        route.delete()

        self.__commit()

    def add_vip(self, vip_name, vip, port):

        network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'Network', cardinality=u'unspecified',locked=u'no',name=u'network',
                                                    scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        nsipfolder = cobra.model.vns.FolderInst(network, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                key=u'nsip', cardinality=u'unspecified', locked=u'no',
                                                name=unicode(vip_name),
                                                scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'ipaddress', cardinality=u'unspecified',
                                  locked=u'no', name=u'ipaddress', value=unicode(vip), validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'hostroute', cardinality=u'unspecified',
                                  locked=u'no',
                                  name=u'hostroute', value=u'ENABLED', validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'netmask', cardinality=u'unspecified', locked=u'no',
                                  name=u'netmask', value=u'255.255.255.255', validation=u'')


        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'dynamicrouting', cardinality=u'unspecified',
                                  locked=u'no', name=u'dynamicrouting', value=u'DISABLED', validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'type', cardinality=u'unspecified', locked=u'no',
                                  name=u'type', value=u'VIP', validation=u'')

        mFCnglbvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'mFCnglbvserver', cardinality=u'unspecified', locked=u'no',
                                                    name=u'mFCnglbvserver-'+unicode(vip_name), scopedBy=u'epg', devCtxLbl=u'',
                                                    nodeNameOrLbl=self.nodeName)

        cobra.model.vns.CfgRelInst(mFCnglbvserver, locked=u'no', name=u'lbvserver_key', key=u'lbvserver_key',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=unicode(vip_name))

        mFCngNetwork = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                 key=u'mFCngNetwork', cardinality=u'unspecified', locked=u'no',
                                                 name=u'mFCngnetwork-'+unicode(vip_name), scopedBy=u'epg',
                                                 devCtxLbl=u'', nodeNameOrLbl=self.nodeName)
        cobra.model.vns.CfgRelInst(mFCngNetwork, locked=u'no', name=u'Network_key', key=u'Network_key',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=u'network/'+unicode(vip_name))


        lbvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                               key=u'lbvserver', cardinality=u'unspecified', locked=u'no', name=unicode(vip_name),
                                               scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)


        internal_network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                      key=u'internal_network', cardinality=u'unspecified', locked=u'no',
                                                      name=u'internal_network-' + unicode(vip_name), scopedBy=u'epg', devCtxLbl=u'',
                                                      nodeNameOrLbl=self.nodeName)
        cobra.model.vns.CfgRelInst(internal_network, locked=u'no', name=u'internal_network_key', key=u'internal_network_key',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=u'network/' + unicode(vip_name))


        cobra.model.vns.ParamInst(lbvserver, mandatory=u'no', key=u'ipv46', cardinality=u'unspecified', locked=u'no',
                                  name=u'ipv4', value=unicode(vip))

        cobra.model.vns.ParamInst(lbvserver, mandatory=u'no', key=u'port', cardinality=u'unspecified', locked=u'no',
                                  name=u'port', value=unicode(port), validation=u'')

        cobra.model.vns.ParamInst(lbvserver, mandatory=u'no', key=u'persistencetype', cardinality=u'unspecified', locked=u'no',
                                  name=u'persistencetype', value=u'NONE')

        cobra.model.vns.ParamInst(lbvserver, mandatory=u'no', key=u'name', cardinality=u'unspecified', locked=u'no',
                                  name=u'name', value=unicode(vip_name))

        self.__commit()

    def add_ssl_vip(self, vip_name, vip, port, certkey):

        network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'Network', cardinality=u'unspecified',locked=u'no',name=u'network',
                                                    scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        nsipfolder = cobra.model.vns.FolderInst(network, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                key=u'nsip', cardinality=u'unspecified', locked=u'no',
                                                name=unicode(vip_name),
                                                scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'ipaddress', cardinality=u'unspecified',
                                  locked=u'no', name=u'ipaddress', value=unicode(vip), validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'hostroute', cardinality=u'unspecified',
                                  locked=u'no',
                                  name=u'hostroute', value=u'ENABLED', validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'netmask', cardinality=u'unspecified', locked=u'no',
                                  name=u'netmask', value=u'255.255.255.255', validation=u'')


        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'dynamicrouting', cardinality=u'unspecified',
                                  locked=u'no', name=u'dynamicrouting', value=u'DISABLED', validation=u'')

        cobra.model.vns.ParamInst(nsipfolder, mandatory=u'no', key=u'type', cardinality=u'unspecified', locked=u'no',
                                  name=u'type', value=u'VIP', validation=u'')

        mFCngsslvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'mFCngsslvserver', cardinality=u'unspecified', locked=u'no',
                                                    name=u'mFCngsslvserver-'+unicode(vip_name), scopedBy=u'epg', devCtxLbl=u'',
                                                    nodeNameOrLbl=self.nodeName)

        cobra.model.vns.CfgRelInst(mFCngsslvserver, locked=u'no', name=u'sslvserver_key', key=u'sslvserver_key',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=unicode(vip_name))

        mFCngNetwork = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                 key=u'mFCngNetwork', cardinality=u'unspecified', locked=u'no',
                                                 name=u'mFCngnetwork-'+unicode(vip_name), scopedBy=u'epg',
                                                 devCtxLbl=u'', nodeNameOrLbl=self.nodeName)
        cobra.model.vns.CfgRelInst(mFCngNetwork, locked=u'no', name=u'Network_key', key=u'Network_key',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=u'network/'+unicode(vip_name))


        sslvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                               key=u'sslvserver', cardinality=u'unspecified', locked=u'no', name=unicode(vip_name),
                                               scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        cobra.model.vns.ParamInst(sslvserver, mandatory=u'no', key=u'ipv46', cardinality=u'unspecified', locked=u'no',
                                  name=u'ipv4', value=unicode(vip))

        cobra.model.vns.ParamInst(sslvserver, mandatory=u'no', key=u'port', cardinality=u'unspecified', locked=u'no',
                                  name=u'port', value=unicode(port), validation=u'')

        cobra.model.vns.ParamInst(sslvserver, mandatory=u'no', key=u'persistencetype', cardinality=u'unspecified', locked=u'no',
                                  name=u'persistencetype', value=u'NONE')

        cobra.model.vns.ParamInst(sslvserver, mandatory=u'no', key=u'name', cardinality=u'unspecified', locked=u'no',
                                  name=u'name', value=unicode(vip_name))


        sslvserver_sslcertkey_binding = cobra.model.vns.FolderInst(sslvserver,  ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                   key=u'sslvserver_sslcertkey_binding', cardinality=u'unspecified', locked=u'no',
                                   name=u'sslvserver_sslcertkey_binding-' + unicode(vip_name), scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        cobra.model.vns.CfgRelInst(sslvserver_sslcertkey_binding, locked=u'no', name=u'certkeyname', key=u'certkeyname',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=unicode(certkey))

        self.__commit()

    def remove_vip(self, vip_name):
        network = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName,graphNameOrLbl=self.graphName,
                                               key=u'Network', cardinality=u'unspecified', locked=u'no',
                                               name=u'network', scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        nsipfolder = cobra.model.vns.FolderInst(network, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                key=u'nsip', cardinality=u'unspecified', locked=u'no',
                                                name=unicode(vip_name),
                                                scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        mFCnglbvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'mFCnglbvserver', cardinality=u'unspecified', locked=u'no',
                                                    name=u'mFCnglbvserver-'+unicode(vip_name), scopedBy=u'epg', devCtxLbl=u'',
                                                    nodeNameOrLbl=self.nodeName)

        mFCngNetwork = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                 key=u'mFCngNetwork', cardinality=u'unspecified', locked=u'no',
                                                 name=u'mFCngnetwork-'+unicode(vip_name), scopedBy=u'epg',
                                                 devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        lbvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                               key=u'lbvserver', cardinality=u'unspecified', locked=u'no', name=unicode(vip_name),
                                               scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)
        nsipfolder.delete()
        mFCnglbvserver.delete()
        mFCngNetwork.delete()
        lbvserver.delete()
        self.__commit()

    def add_service_group(self,sg_name, port):
        sg_name = unicode(sg_name)
        port = unicode(port)

        mFCngservicegroup = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                       key=u'mFCngservicegroup', cardinality=u'unspecified', locked=u'no',
                                                       name=u'mFCngservicegroup-' + sg_name, scopedBy=u'epg', devCtxLbl=u'',
                                                       nodeNameOrLbl=self.nodeName)

        cobra.model.vns.CfgRelInst(mFCngservicegroup, locked=u'no',name=u'servicegroup_key',  key=u'servicegroup_key',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=sg_name)

        servicegroup = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName,graphNameOrLbl=self.graphName,
                                                  key=u'servicegroup', cardinality=u'unspecified', locked=u'no', name=sg_name,
                                                  scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)


        cobra.model.vns.ParamInst(servicegroup, mandatory=u'no', key=u'servicegroupname', cardinality=u'unspecified',
                                                 locked=u'no', name=u'servicegroupname', value=sg_name)

        cobra.model.vns.ParamInst(servicegroup, mandatory=u'no', key=u'port', cardinality=u'unspecified',
                                                 locked=u'no', name=u'port', value=port)

        self.__commit()

    def remove_service_group(self,sg_name):
        sg_name = unicode(sg_name)

        mFCngservicegroup = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                       key=u'mFCngservicegroup', cardinality=u'unspecified', locked=u'no',
                                                       name=u'mFCngservicegroup-' + sg_name, scopedBy=u'epg', devCtxLbl=u'',
                                                       nodeNameOrLbl=self.nodeName)


        servicegroup = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName,graphNameOrLbl=self.graphName,
                                                  key=u'servicegroup', cardinality=u'unspecified', locked=u'no', name=sg_name,
                                                  scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        mFCngservicegroup.delete()
        servicegroup.delete()

        self.__commit()

    def add_server_to_service_group(self, sg_name, name, ip):
        sg_name = unicode(sg_name)
        servicegroup = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName,graphNameOrLbl=self.graphName,
                                                  key=u'servicegroup', cardinality=u'unspecified', locked=u'no', name=sg_name,
                                                  scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)


        name = unicode(name)
        ip = unicode(ip)
        servicegroupmember_binding = cobra.model.vns.FolderInst(servicegroup, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                                    key=u'servicegroup_servicegroupmember_binding', cardinality=u'unspecified',
                                                                    locked=u'no', name=name + '_binding', scopedBy=u'epg', devCtxLbl=u'',
                                                                    nodeNameOrLbl=self.nodeName)
        cobra.model.vns.ParamInst(servicegroupmember_binding, mandatory=u'no',
                                      key=u'ip', cardinality=u'unspecified', locked=u'no',
                                      name=u'ip', value=ip)
        self.__commit()

    def remove_server_from_service_group(self, sg_name, name, ip):
        sg_name = unicode(sg_name)
        servicegroup = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName,graphNameOrLbl=self.graphName,
                                                  key=u'servicegroup', cardinality=u'unspecified', locked=u'no', name=sg_name,
                                                  scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)


        name = unicode(name)
        ip = unicode(ip)
        servicegroupmember_binding = cobra.model.vns.FolderInst(servicegroup, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                                    key=u'servicegroup_servicegroupmember_binding', cardinality=u'unspecified',
                                                                    locked=u'no', name=name + '_binding', scopedBy=u'epg', devCtxLbl=u'',
                                                                    nodeNameOrLbl=self.nodeName)

        server = cobra.model.vns.ParamInst(servicegroupmember_binding, mandatory=u'no',
                                      key=u'ip', cardinality=u'unspecified', locked=u'no',
                                      name=u'ip', value=ip)
        server.delete()
        servicegroupmember_binding.delete()
        self.__commit()

    def add_ssl_cert_key_pair(self, cert_name, key_name, key_pair_name, password):
        cert_name = unicode(cert_name)
        key_name = unicode(key_name)
        key_pair_name = unicode(key_pair_name)
        password = unicode(password)

        sslcertkey = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'sslcertkey', cardinality=u'unspecified',locked=u'no',name=key_pair_name,
                                                    scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        cobra.model.vns.ParamInst(sslcertkey, key=u'cert', cardinality=u'unspecified', locked=u'no', name=u'cert',
                                  value=cert_name)
        cobra.model.vns.ParamInst(sslcertkey, key=u'key', cardinality=u'unspecified', locked=u'no', name=u'key',
                                  value=key_name)
        cobra.model.vns.ParamInst(sslcertkey, key=u'certkey', cardinality=u'unspecified', locked=u'no', name=u'certkey',
                                  value=key_pair_name)
        cobra.model.vns.ParamInst(sslcertkey, key=u'passplain', cardinality=u'unspecified', locked=u'no', name=u'passplain',
                                  value=password)

        mFCngsslcertkey = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                                    key=u'mFCngsslcertkey', cardinality=u'unspecified', locked=u'no',
                                                    name=u'mFCngsslcertkey-' + key_pair_name, scopedBy=u'epg', devCtxLbl=u'',
                                                    nodeNameOrLbl=self.nodeName)

        cobra.model.vns.CfgRelInst(mFCngsslcertkey, name='sslcertkey_key', key='sslcertkey_key',
                                   targetName=key_pair_name)



        self.__commit()


    def map_sg_vip(self,service_group_name,lbserver_name):
        sg= unicode(service_group_name)

        lbvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                               key=u'lbvserver', cardinality=u'unspecified', locked=u'no', name=unicode(lbserver_name),
                                               scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        lbvserver_sg_binding = cobra.model.vns.FolderInst(lbvserver,  ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                   key=u'lbvserver_servicegroup_binding', cardinality=u'unspecified', locked=u'no',
                                   name=u'servicegroup_servicegroupmember_binding-' + sg, scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        cobra.model.vns.CfgRelInst(lbvserver_sg_binding, locked=u'no', name=u'servicename', key=u'servicename',
                                   mandatory=u'no', cardinality=u'unspecified', targetName=unicode(service_group_name))

        self.__commit()

    def unmap_sg_vip(self,service_group_name,lbserver_name):

        servicegroup_binding = unicode(service_group_name + '_' + lbserver_name + '_binding')

        lbvserver = cobra.model.vns.FolderInst(self.fvAEPg, ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                               key=u'lbvserver', cardinality=u'unspecified', locked=u'no', name=unicode(lbserver_name),
                                               scopedBy=u'epg', devCtxLbl=u'', nodeNameOrLbl=self.nodeName)

        lbvserver_sg_binding = cobra.model.vns.FolderInst(lbvserver,  ctrctNameOrLbl=self.ctrctName, graphNameOrLbl=self.graphName,
                                   key=u'lbvserver_servicegroup_binding', cardinality=u'unspecified', locked=u'no',
                                   name=servicegroup_binding, scopedBy=u'epg', devCtxLbl=u'',nodeNameOrLbl=self.nodeName)

        lbvserver_sg_binding.delete()
        self.__commit()

    def __commit(self):
        #print toXMLStr(topMo)
        c = cobra.mit.request.ConfigRequest()
        c.addMo(self.topMo)
        self.md.commit(c)

