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
    ctx = nodechecker.context.Context()
    this_node = nodechecker.node.Node()
    ctx.this_node = this_node

''' to itegration tets
def test_start_stop():
    print("ENTER test_start_stop()")
    global conf, resource_lock, ctx

    worker = nodechecker.worker.Worker(ctx, resource_lock)
    assert worker.isAlive() is False

    worker.start()
    assert worker.isAlive() is True

    worker.shutdown()
    #time.sleep(5)
    #assert worker.isAlive() is False
    print("ENTER test_start_stop()")
'''

def test_master_election_become_master():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]    
    worker = nodechecker.worker.Worker(ctx, resource_lock)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    worker._udp_listener = udp_listener
    
    worker._listen_to_master_heartbeats = MagicMock()
    worker._listen_to_master_heartbeats.return_value = "TOO_LOW"
    
    worker._become_a_master = MagicMock()
    worker._become_slave = MagicMock()
    
    print ("master_election")

    worker.master_election()
    master = worker._become_a_master.assert_called_once_with()
    
    
def test_master_election_become_slave():
    global conf, resource_lock, ctx
    print ("enter test_udp_listener_master_election")

    ctx.active_node_list = [ctx.this_node]    
    worker = nodechecker.worker.Worker(ctx, resource_lock)
    
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    udp_listener.run = MagicMock()
    udp_listener.shutdown = MagicMock()
    worker._udp_listener = udp_listener
    
    worker._listen_to_master_heartbeats = MagicMock()
    worker._listen_to_master_heartbeats.return_value = "TOO_HIGH"
    
    worker._become_a_master = MagicMock()
    worker._become_a_slave = MagicMock()
    
    print ("master_election")

    worker.master_election()
    master = worker._become_a_slave.assert_called_once_with()
    
    
    
    

    

    
    

    






