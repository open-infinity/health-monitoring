import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.manager
import nodechecker.context
import nodechecker.udp_listener
import nodechecker.timers
from mock import MagicMock
import time


conf = None
runtime = None
resource_lock = None
context = None


def setup():
    global resource_lock, context
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()

    context = nodechecker.context.Context()
    context.this_node = this_node
    context.resource_lock = resource_lock


def test_start_stop():
    global resource_lock, context

    manager = nodechecker.manager.Manager(context)
    assert manager.isAlive() is False

    manager.start()
    assert manager.isAlive() is True

    manager.shutdown()
    manager.join()
    assert manager.isAlive() is False

'''
def test_send_receive_heartbeats():
    global resource_lock, context

    # Setup
    listener_node = nodechecker.node.Node(ip_address='5.5.5.5', port=11111)
    ctx2 = nodechecker.context.Context()
    ctx2.this_node = listener_node
    ctx2.resource_lock = resource_lock
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx2)
    
    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111)
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911)
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911)
    context.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911)
    context.node_list = [n1, n2, n3, context.this_node]
    context.heartbeat_period = 1

    # Run
    udp_listener.start()
    #nodechecker.manager.send_heartbeats(context)
    nodechecker.timers.timer_heartbeat_start(context)
    time.sleep(context.heartbeat_period * 3)

    # Verification
    assert context.master_list[0] == context.this_node

    # Tear down
    nodechecker.timers.cancel(context)
    context.timer_heartbeat.join()
    udp_listener.shutdown()
    udp_listener.join()
'''







