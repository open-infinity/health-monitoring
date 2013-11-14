#!/usr/bin/env python2

import sys
import logging
import node
import util


class Reader(object):
    def __init__(self, nodelist_file):
        self.nodelist_file = nodelist_file
        self.node_list = []
        self.node_attributes = ['IP_ADDRESS', 'IP_ADDRESS_PUBLIC', 'HOST_NAME',
                                'MACHINE_TYPE', 'MACHINE_ID', 'GROUP_NAME']
        self.logger = logging.getLogger('nodechecker.reader')

    def get_node_list(self, my_node, mode):
        node_list = []
        try:
            with open(self.nodelist_file, 'r') as f:
                i = 0
                for line in f.readlines():
                    if len(line) > 1:
                        node_data_list = line.split(None)
                        if mode == "TEST":
                            my_node.port = 11911 + i
                        i += 1
                        node_list.append(node.Node(
                              port=my_node.port,
                              ip_address=node_data_list[0],
                              hostname=node_data_list[2],
                              machine_type=node_data_list[3],
                              ip_address_public=node_data_list[1],
                              instance_id=my_node.instance_id,
                              cluster_id=my_node.cluster_id,
                              machine_id=node_data_list[4],
                              cloud_zone=my_node.cloud_zone))
        except:
            util.log_exception(sys.exc_info())
        return node_list

    def get_attribute(self, ip_address, attr_type):
        try:
            attr_pos = self.node_attributes.index(attr_type)
            attr_ip_pos = self.node_attributes.index('IP_ADDRESS')
            with open(self.nodelist_file, 'r') as f:
                for line in f.readlines():
                    if len(line) > 1:
                        node_data_list = line.split(None)
                        if ip_address == node_data_list[attr_ip_pos]:
                            return node_data_list[attr_pos]
        except:
            util.log_exception(sys.exc_info())
