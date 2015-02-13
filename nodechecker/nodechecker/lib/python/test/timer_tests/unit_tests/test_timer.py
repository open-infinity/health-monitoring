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


def test_dead_node_scanner_start_stop_with_node_creation_verifiers():
    global resource_lock, ctx

    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111, hostname='n1')
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911, hostname='n2')
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911, hostname='n3')
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911, hostname='n4')
    ctx.node_list = [n1, n2, n3, ctx.this_node]

    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    p1_dir = os.path.abspath(os.path.join(test_dir, os.pardir))
    p2_dir = os.path.abspath(os.path.join(p1_dir, os.pardir))
    ctx.conf = nodechecker.config.Config(os.path.join(p2_dir, 'conf', 'nodechecker', 'etc', 'nodechecker.conf'))
    ctx.NODE_CREATION_TIMEOUT = 10

    ctx.ntf_manager = MagicMock()
    ctx.dead_node_timeout = 0.01
    print(ctx.conf.collectd_rrd_dir)
    dead_node_scanner = nodechecker.timer.DeadNodeScanner(ctx)

    dead_node_scanner.start()
    time.sleep(ctx.dead_node_timeout * 10)
    dead_node_scanner.cancel()
    pending_timers_list = dead_node_scanner.node_creation_verifier_list
    dead_node_scanner.join()
    assert dead_node_scanner.isAlive() is False
    assert len(pending_timers_list) == 0

