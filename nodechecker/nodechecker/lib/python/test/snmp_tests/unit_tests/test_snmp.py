
import os
import inspect
import nodechecker.notification.notification
import nodechecker.notification.snmp
import nodechecker.config
import nodechecker.node

node = None
conf = None
sender = None


def setup():
    global node, conf, sender
    node = nodechecker.node.Node(hostname='test1', port=10, cloud_zone='cloudzone1', ip_address_public='1.2.3.4',
                                     instance_id=1, cluster_id=1, machine_id=1)
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    p1_dir = os.path.abspath(os.path.join(test_dir, os.pardir))
    p2_dir = os.path.abspath(os.path.join(p1_dir, os.pardir))
    conf = nodechecker.config.Config(os.path.join(p2_dir, 'conf', 'nodechecker', 'etc', 'nodechecker.conf'))
    #conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))
    sender = nodechecker.notification.snmp.TrapSender(conf, node)


def test_send():
    global node, conf, sender
    ntf_1 = nodechecker.notification.notification.Notification(category='fatal', severity='error')
    ntf_2 = nodechecker.notification.notification.Notification(category='dead', severity='warn')

    notifications = [ntf_1, ntf_2]
    error = 0
    try:
        sender.send(notifications)
    except Exception:
        error = 1
    assert error == 0


def test_truncate():
    global node, conf, sender
    word_1 = ''
    word_2 = '123456789'
    word_3 = 3

    assert sender.truncate(word_1, 0) == ''
    assert sender.truncate(word_1, 1) == ''
    assert sender.truncate(word_2, 0) == ''
    assert sender.truncate(word_2, 1) == '1'
    assert sender.truncate(word_2, 9) == '123456789'
    assert sender.truncate(word_2, 10) == '123456789'

    # should throw TypeError exception
    thrown = False
    try:
        sender.truncate(word_3, 0) == ''
    except TypeError:
        thrown = True
    assert thrown is True
