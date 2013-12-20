#!/usr/bin/env python2

import os
import sys
import time
import logging
import notification
import nodechecker.util

OI_HEALTH_MONITORING_ROOT = "OI_HEALTH_MONITORING_ROOT"


class NotificationReader(object):

    def __init__(self, node, config):
        self.logger = logging.getLogger('nodechecker.notificationreader')
        self.node = node
        self.dead_node_string = config.notifications_dead_node_string
        self.eol = "\n"
        self.text_separator = ":"
        self.inbox = os.path.join(os.environ[OI_HEALTH_MONITORING_ROOT],
                                  config.notifications_home,
                                  config.notifications_inbox_dir)

    def get_notifications(self, node_list):
        try:
            new_notifications_list = []
            for file_name in os.listdir(self.inbox):
                ntfc = self.parse(file_name, node_list)
                new_notifications_list.append(ntfc)
        except:
            nodechecker.util.log_exception(sys.exc_info())
        return new_notifications_list

    def parse(self, file_name, node_list):
        ntfc = notification.Notification()
        ntfc.file_path = os.path.join(self.inbox, file_name)
        ntfc.file_name = file_name
        with open(ntfc.file_path) as f:
            for line in f:
                result_list = line.strip(self.eol).split(self.text_separator)
                # This is a line with 'key: value' format
                if len(result_list) == 2:
                    key = result_list[0]
                    value = result_list[1]
                    #print ("key", key, "   ", "value", value)
                    if key == 'Severity':
                        ntfc.severity = value
                    if key == 'Time':
                        ntfc.time = time.asctime(time.gmtime(float(value)))
                    if key == 'Host':
                    # FIXME: strip whitespace at start from all values,
                    # not just for hostname
                        ntfc.hostname = value[1:]
                    if key == 'Plugin':
                        ntfc.plugin = value
                    if key == 'PluginInstance':
                        ntfc.plugin_instance = value
                    if key == 'Type':
                        ntfc.meteric_type = value
                    if key == 'TypeInstance':
                        ntfc.metric_type_instance = value
                    if key == 'DataSource':
                        ntfc.data_source = value
                    if key == 'CurrentValue':
                        ntfc.current_value = value
                    if key == 'WarningMin':
                        ntfc.warning_min = value
                    if key == 'WarningMax':
                        ntfc.warning_max = value
                    if key == 'FailureMin':
                        ntfc.failure_min = value
                    if key == 'FailureMax':
                        ntfc.failure_max = value
                    else:
                        ntfc.message = key + ' ' + value
                        ntfc.category = 'METRIC_OUT_OF_RANGE'

                elif len(result_list) == 1 and len(result_list[0]) > 1:
                    ntfc.message = result_list[0]
                    ntfc.category = 'METRIC_UPDATE_NOK'
                else:
                    pass

        for n in node_list:
            if n.hostname == self.node.hostname:
                ntfc.add_master_node_parameters(n)
                return ntfc
        return None
