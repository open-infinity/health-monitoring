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
    ctx.conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))
    ctx.NODE_CREATION_TIMEOUT = 10

    ctx.ntf_manager = MagicMock()
    ctx.dead_node_timeout = 0.01
    print(ctx.conf.collectd_rrd_dir)
    dead_node_scanner = nodechecker.timer.DeadNodeScanner(ctx)

    dead_node_scanner.start()
    time.sleep(ctx.dead_node_timeout * 10)
    pending_timers_list = dead_node_scanner.cancel()
    dead_node_scanner.join()
    assert dead_node_scanner.isAlive() is False
    assert len(pending_timers_list) == 0


def test_node_state():
    
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    test_parent_dir = os.path.abspath(os.path.join(test_dir, os.pardir))
    
    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111, hostname='n1')
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911, hostname='n2')
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911, hostname='n3')
    
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911, hostname='test-host')
    ctx.node_list = [n1, n2, n3, ctx.this_node]
    ctx.active_node_list = [n1, n2, n3, ctx.this_node]
    ctx.dead_node_set = None
    ctx.conf.collectd_rrd_dir = os.path.join(test_parent_dir, "data", "rrd")
    ctx.conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))
    ctx.dead_node_timeout = 10
    
    rrd_data_path = os.path.join(test_parent_dir, "data", "rrd")
    # <lastupdate>1416251047</lastupdate> <!-- 2014-11-17 21:04:07 EET -->
    last_update = 1416251047
    
    dead_node_scanner = nodechecker.timer.DeadNodeScanner(ctx)
    
    assert "CHANGED_TO_DEAD" == dead_node_scanner._node_state(rrd_data_path, last_update + ctx.dead_node_timeout + 1, False)    
    assert "NOT_CHANGED" == dead_node_scanner._node_state(rrd_data_path, last_update + ctx.dead_node_timeout + 1, True)
    assert "CHANGED_TO_ALIVE" == dead_node_scanner._node_state(rrd_data_path, last_update + ctx.dead_node_timeout - 1 , True)
