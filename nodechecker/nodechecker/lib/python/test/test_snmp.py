import nodechecker
import nodechecker.notifier.notification
import nodechecker.notifier.snmp
import nodechecker.config
import nodechecker.node

def test_trap_send():
	node = nodechecker.node.Node(hostname='test1', port=10, cloud_zone='cloudzone1',ip_address_public='1.2.3.4',
		instance_id=1, cluster_id=1, machine_id=1)
	conf = nodechecker.config.Config("test/nodechecker.conf")
	sender = nodechecker.notifier.snmp.TrapSender(conf, node)
	ntf_1 = nodechecker.notifier.notification.Notification()
	ntf_2 = nodechecker.notifier.notification.Notification()

	notifications = [ntf_1, ntf_2]
	error = sender.send(notifications)

	assert error == 0
