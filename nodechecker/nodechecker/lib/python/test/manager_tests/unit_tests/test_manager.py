import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.manager
import time
import nodechecker.context
import nodechecker.udp_listener
from mock import MagicMock


conf = None
runtime = None
resource_lock = None
ctx = None

HB_PERIOD_IN_SEC = 0.001

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
    manager = nodechecker.manager.Manager(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    manager._udp_listener = udp_listener
    
    manager._get_master_count = MagicMock()
    manager._get_master_count.return_value = "TOO_LOW"
    
    manager._become_a_master = MagicMock()
    manager._become_slave = MagicMock()
    
    print ("master_election")

    index = manager._master_election(0)
    assert index == 0
    manager._become_a_master.assert_called_once_with()
    
    
def test_master_election_become_slave():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]    
    manager = nodechecker.manager.Manager(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    manager._udp_listener = udp_listener
    
    manager._get_master_count = MagicMock()
    manager._get_master_count.return_value = "TOO_HIGH"
    
    manager._become_a_master = MagicMock()
    manager._become_a_slave = MagicMock()
    
    print ("master_election")

    manager._master_election(0)
    manager._become_a_slave.assert_called_once_with()


def test_get_master_count_with_role_master_and_0_master_hbs_received():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]  
    ctx.heartbeat_period = 0
    ctx.this_node.role = "MASTER"
  
    manager = nodechecker.manager.Manager(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    manager._udp_listener = udp_listener
    
    res = manager._get_master_count(1)
    
    assert res == "FINE"


def test_get_master_count_with_role_slave_and_0_master_hbs_received():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]  
    ctx.heartbeat_period = 0
    ctx.this_node.role = "SLAVE"
  
    manager = nodechecker.manager.Manager(ctx)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    manager._udp_listener = udp_listener
    
    res = manager._get_master_count(1)
    
    assert res == "TOO_LOW"   


def test_send_heartbeats_with_cancel():
    # Setup
    manager = nodechecker.manager.Manager(ctx)
    nodechecker.manager.send = MagicMock()
    ctx.heartbeat_period = HB_PERIOD_IN_SEC

    #Run
    nodechecker.manager.send_heartbeats(ctx)
    time.sleep(ctx.heartbeat_period * 3)

    # Verification
    assert nodechecker.manager.send.call_count > 1

    # Tear down
    manager._cancel_timers()


def test_start_dead_node_scan_timer_with_cancel():
    # Setup
    manager = nodechecker.manager.Manager(ctx)
    manager._dead_node_scan = MagicMock()
    ctx.rrd_scan_period = 0.001

    # Run
    manager._start_dead_node_scan_timer()
    time.sleep(ctx.rrd_scan_period * 3)

    # Verification
    assert manager._dead_node_scan.call_count > 1

    # Tear down
    manager._cancel_timers()




