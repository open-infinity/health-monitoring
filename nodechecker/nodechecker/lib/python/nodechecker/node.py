#!/usr/bin/env python2

import json
import hashlib


class Node(object):
    """This class represents health monitoring node."""
    def __init__(self,
                 port=None,
                 ip_address=None,
                 ip_address_public=None,
                 instance_id=None,
                 cluster_id=None,
                 machine_id=None,
                 cloud_zone=None,
                 role="SLAVE",
                 hostname=None,
                 machine_type="NOT_DEFINED"):
        self.role = role
        self.hostname = hostname
        self.ip_address = ip_address
        self.ip_address_public = ip_address_public
        self.instance_id = instance_id
        self.cluster_id = cluster_id
        self.machine_id = machine_id
        self.cloud_zone = cloud_zone
        self.port = int(port)
        self.machine_type = machine_type
        self.group_name = "oi"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.ip_address == other.ip_address
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.ip_address < other.ip_address or self.port < other.port

    def __hash__(self):
        h = hashlib.md5()
        h.update(self.ip_address)
        a = h.hexdigest()
        return int(a, 16)

    def to_json(self):
        return json.dumps(
        ["node", {"ip_address": self.ip_address,
                  "hostname": self.hostname,
                  "role": self.role,
                  "port": self.port,
                  "machine_type": self.machine_type
        }])

    def from_json(self, json_data):
        json_object = json.loads(json_data)
        self.role = json_object[1]["role"]
        self.hostname = json_object[1]["hostname"]
        self.ip_address = json_object[1]["ip_address"]
        self.port = int(json_object[1]["port"])
        self.machine_type = json_object[1]["machine_type"]
        return self

    def to_dict(self):
        return {"ip_address": self.ip_address,
                "hostname": self.hostname,
                "role": self.role,
                "port": self.port,
                "machine_type": self.machine_type}

    def from_dict(self, node_dict):
        self.role = node_dict["role"]
        self.hostname = node_dict["hostname"]
        self.ip_address = node_dict["ip_address"]
        self.port = int(node_dict["port"])
        self.machine_type = node_dict["machine_type"]
        return self

    def __repr__(self):
        return "node %s %s %s %s %s" % (
              self.role, self.hostname, self.ip_address, self.port,
              self.machine_type)


def node_list_from_dict_list(dict_list):
    output_list = []
    for item in dict_list:
        output_list.append(node_from_dict(item))
    return output_list


def node_from_dict(dict_item):
    return Node(int(dict_item["port"]),
                    dict_item["ip_address"],
                    dict_item["role"],
                    dict_item["hostname"],
                    dict_item["machine_type"])
