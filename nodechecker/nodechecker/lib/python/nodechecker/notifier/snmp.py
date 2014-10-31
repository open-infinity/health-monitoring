import logging
import subprocess
import nodechecker.util
import sys


class TrapSender(object):
    def __init__(self, conf, node):
        self.logger = logging.getLogger('nodechecker.mailsender')
        self.logger.info('creating an instance of nodechecker.mailsender')
        self.conf = conf
        self.node = node

    def send(self, notification_list, snmp_version = 2):
        if notification_list:
            for n in notification_list:
                if snmp_version == '1':
                    self.send_snmp_v1_trap(n)
                elif snmp_version == '2c':
                    self.send_snmp_v2c_trap(n)
                elif snmp_version == '3':
                    self.send_snmp_v3_trap(n)
                else:
                    self.logger.error("Invalid SNMP version: " + snmp_version)
                pass

    def send_snmp_v1_trap(self, notification):
        pass
        # TODO   subprocess.Popen(['snmptrap', '-v', '1'])

    def send_snmp_v2c_trap(self, notification):
        smnptrap = subprocess.Popen([
            'snmptrap',
            '-v', '2c',
            '-c', self.conf.snmp_community_string, self.conf.manager,
            self.truncate(self.node.hostname, 255),
            'OI-HM-MIB::notification',
            'nodeHostname', 's', self.truncate(self.node.hostname, 255),
            'nodeCloudZone', 's', self.truncate(self.node.cloud_zone, 255),
            'nodeIpAddressPublic', 's', self.node.ip_address_public,
            'nodeInstanceId', 'u', self.node.instance_id,
            'nodeClusterId', 'u', self.node.cluster_id,
            'nodeMachineId', 'u', self.node.machine_id,
            'ntfCategory', 's', self.truncate(notification.category, 15),
            'ntfSeverity', 's', self.truncate(notification.severity), 15,
            'ntfTime', 't', notification.time,
            'ntfMessage', 's', self.truncate(notification.message, 511),
            'ntfHostname', 's', self.truncate(notification.hostname, 63),
            'ntfMachineId', 'u', notification.machine_id,
            'ntfIpAddressPublic', 's', notification.ip_address_public],
            stderr=subprocess.PIPE)
        msg = smnptrap.communicate()[0]
        if len(msg) > 0:
            self.logger.error(msg)

    def send_snmp_v3_trap(self, notification):
        try:
            pass
            # TODO subprocess.Popen(['snmptrap',])

        except:
            nodechecker.util.log_exception(sys.exc_info())

    def truncate(self, str, max_len):
        return (str[:max_len]) if len(str) > max_len else str

