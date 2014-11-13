#!/usr/bin/env python2


class Notification(object):
    _MSG_DEAD_NODE = "Lost contact with host"
    _MSG_RESURRECTED_NODE = "Found node that resurrected from dead"

    def __init__(self, category='', severity='', file_name='', file_path='',
                 metric_type='', time='', hostname='', ip_address_public='',
                 machine_id='', plugin='', plugin_instance='', metric_type_instance='',
                 data_source='', current_value='', warning_min='', warning_max='',
                 failure_min='', failure_max='', message='', ):
        self.category = category
        self.severity = severity
        self.file_name = file_name
        self.file_path = file_path
        self.metric_type = metric_type
        self.time = time
        self.hostname = hostname
        self.ip_address_public = ip_address_public
        self.machine_id = machine_id
        self.plugin = plugin
        self.plugin_instance = plugin_instance
        self.metric_type = metric_type
        self.metric_type_instance = metric_type_instance
        self.data_source = data_source
        self.current_value = current_value
        self.warning_min = warning_min
        self.warning_max = warning_max
        self.failure_min = failure_min
        self.failure_max = failure_max
        self.message = message

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

    def add_origin_node_parameters(self, origin_node):
        self.ip_address_public = origin_node.ip_address_public
        self.machine_id = origin_node.machine_id
        return self


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
