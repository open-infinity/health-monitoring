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

	def send(self, notification_list, snmp_version = '2c'):
		error = 0
		for n in notification_list:
			if snmp_version == '1':
				error = self.send_snmp_v1_trap(n)
			elif snmp_version == '2c':
				error = self.send_snmp_v2c_trap(n)
			elif snmp_version == '3':
				error = self.send_snmp_v3_trap(n)
			else:
				error = 1
				self.logger.error("Invalid SNMP version: " + snmp_version)
			return error

	def send_snmp_v1_trap(self, notification):
		pass
		# TODO   subprocess.Popen(['snmptrap', '-v', '1'])
		return 0

	def send_snmp_v2c_trap(self, notification):
		error = 0;
		smnptrap = subprocess.Popen([
			'snmptrap','-v', '2c',
			'-c', self.conf.snmp_community_string,
			self.conf.snmp_manager,
			self.truncate(self.node.hostname, 255),
			'OI-HM-MIB::notification',
			'nodeHostname', 's', self.truncate(self.node.hostname, 255),
			'nodeCloudZone', 's', self.truncate(self.node.cloud_zone, 255),
			'nodeIpAddressPublic', 's', self.node.ip_address_public,
			'nodeInstanceId', 'u', str(self.node.instance_id),
			'nodeClusterId', 'u', str(self.node.cluster_id),
			'nodeMachineId', 'u', str(self.node.machine_id),
			'ntfCategory', 's', self.truncate(notification.category, 15),
			'ntfSeverity', 's', self.truncate(notification.severity, 15),
			'ntfTime', 't', notification.time,
			'ntfMessage', 's', self.truncate(notification.message, 511),
			'ntfHostname', 's', self.truncate(notification.hostname, 63),
			'ntfMachineId', 'u', notification.machine_id,
			'ntfIpAddressPublic', 's', notification.ip_address_public],
			stderr=subprocess.PIPE)
		msg = smnptrap.communicate()[0]
		if msg:
			self.logger.error(msg)
			error = 1
		return error    

	def send_snmp_v3_trap(self, notification):
		try:
			pass
			# TODO subprocess.Popen(['snmptrap',])

		except:
			nodechecker.util.log_exception(sys.exc_info())
		return 0

	def truncate(self, word, max_len):
		return (word[:max_len]) if len(word) > max_len else word
