import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.worker
import time
import nodechecker.context
import nodechecker.udp_listener
from mock import MagicMock


conf = None
runtime = None
resource_lock = None
ctx = None


def setup():
    global conf, resource_lock, ctx
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()
    ctx = nodechecker.context.Context()
    ctx.this_node = this_node
    ctx.resource_lock = resource_lock



def test_master_election_become_master():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]    
    worker = nodechecker.worker.Worker(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    worker._udp_listener = udp_listener
    
    worker._get_master_count = MagicMock()
    worker._get_master_count.return_value = "TOO_LOW"
    
    worker._become_a_master = MagicMock()
    worker._become_slave = MagicMock()
    
    print ("master_election")

    index = worker._master_election(0)
    assert index == 0
    worker._become_a_master.assert_called_once_with()
    
    
def test_master_election_become_slave():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]    
    worker = nodechecker.worker.Worker(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    worker._udp_listener = udp_listener
    
    worker._get_master_count = MagicMock()
    worker._get_master_count.return_value = "TOO_HIGH"
    
    worker._become_a_master = MagicMock()
    worker._become_a_slave = MagicMock()
    
    print ("master_election")

    worker._master_election(0)
    worker._become_a_slave.assert_called_once_with()


def test_get_master_count_with_role_master_and_0_master_hbs_received():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]  
    ctx.heartbeat_period = 0
    ctx.this_node.role = "MASTER"
  
    worker = nodechecker.worker.Worker(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    worker._udp_listener = udp_listener
    
    res = worker._get_master_count(1)
    
    assert res == "FINE"


def test_get_master_count_with_role_slave_and_0_master_hbs_received():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]  
    ctx.heartbeat_period = 0
    ctx.this_node.role = "SLAVE"
  
    worker = nodechecker.worker.Worker(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    worker._udp_listener = udp_listener
    
    res = worker._get_master_count(1)
    
    assert res == "TOO_LOW"   


def test_send_heartbeats_with_cancel():
    worker = nodechecker.worker.Worker(ctx)
    worker._send = MagicMock()
    ctx.heartbeat_period = 0.001
    worker._send_heartbeats()
    time.sleep(0.003)
    worker._cancel_timers()
    assert worker._send.call_count > 1


def test_start_dead_node_scan_timer_with_cancel():
    worker = nodechecker.worker.Worker(ctx)
    worker._dead_node_scan = MagicMock()
    ctx.rrd_scan_period = 0.001
    worker._start_dead_node_scan_timer()
    time.sleep(0.003)
    worker._cancel_timers()
    assert worker._dead_node_scan.call_count > 1




