#!/usr/bin/env python2

import nodechecker


class Notification(object):
    _MSG_DEAD_NODE = "Lost contact with host"
    _MSG_RESURRECTED_NODE = "Found node that resurrected from dead"

    def __init__(self):
        self.category = ""
        self.severity = ""
        self.file_name = ""
        self.file_path = ""
        self.metric_type = ""
        self.time = ""
        self.hostname = ""
        self.ip_address_public = ""
        self.machine_id = ""
        self.plugin = ""
        self.plugin_instance = ""
        self.metric_type = ""
        self.metric_type_instance = ""
        self.data_source = ""
        self.current_value = ""
        self.warning_min = ""
        self.warning_max = ""
        self.failure_min = ""
        self.failure_max = ""
        self.message = ""

    def from_node(self, node, category):
        self.hostname = node.hostname
        self.category = category
        self.ip_address_public = node.ip_address_public
        self.machine_id = node.machine_id

        if category == "DEAD_NODE":
            self.message = self._MSG_DEAD_NODE
            self.severity = "FAILURE"

        elif category == "RESURRECTED_NODE":
            self.message = self._MSG_RESURRECTED_NODE
            self.severity = "INFO"

        return self

    def add_master_node_parameters(self, origin_node):
        self.ip_address_public = origin_node.ip_address_public
        self.machine_id = origin_node.machine_id
        return self


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
