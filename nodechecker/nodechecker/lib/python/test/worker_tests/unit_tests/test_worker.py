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
    master = worker._become_a_slave.assert_called_once_with()






