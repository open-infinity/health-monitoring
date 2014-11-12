import os
import threading
import time

import nodechecker.config
import nodechecker.node

import nodechecker.timer
import nodechecker.context
import nodechecker.timer
import nodechecker.udp_listener

from mock import MagicMock, inspect


conf = None
runtime = None
resource_lock = None
ctx = None


def setup():
    global resource_lock, ctx
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()

    ctx = nodechecker.context.Context()
    ctx.this_node = this_node
    ctx.resource_lock = resource_lock

'''
def test_send_receive_heartbeats():
    global resource_lock, ctx
    send_period_sec = 0.001

    # Setup
    listener_node = nodechecker.node.Node(ip_address='5.5.5.5', port=11111)
    ctx2 = nodechecker.context.Context()
    ctx2.this_node = listener_node
    ctx2.resource_lock = resource_lock
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx2)

    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111)
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911)
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911)
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911)
    ctx.node_list = [n1, n2, n3, ctx.this_node]
    heartbeat_sender = nodechecker.timer.HeartBeatSender(send_period_sec,
                                                         [ctx])

    # Run
    udp_listener.start()
    heartbeat_sender.start()
    time.sleep(send_period_sec * 2)
    heartbeat_sender.cancel()
    udp_listener.shutdown()

    # Verification
    assert ctx2.master_list[0] == ctx.this_node
'''


def test_dead_node_scanner_start_stop():
    global resource_lock, ctx

    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111, hostname='n1')
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911, hostname='n2')
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911, hostname='n3')
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911, hostname='n4')
    ctx.node_list = [n1, n2, n3, ctx.this_node]

    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    ctx.conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))
    ctx.NODE_CREATION_TIMEOUT = 4

    ctx.ntf_manager = MagicMock()
    print(ctx.conf.collectd_rrd_dir)
    scan_period = 1
    dead_node_scanner = nodechecker.timer.DeadNodeScanner(scan_period, ctx)
    #dead_node_scanner._dead_node_scan = MagicMock()

    dead_node_scanner.start()
    time.sleep(scan_period * 2)
    dead_node_scanner.cancel()
    dead_node_scanner.join()
    assert dead_node_scanner.isAlive() is False
