import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.worker
import nodechecker.context
import nodechecker.udp_listener
from mock import MagicMock
import time


conf = None
runtime = None
resource_lock = None
ctx = None


def setup():
    global resource_lock, ctx
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()

    ctx = nodechecker.context.Context()
    ctx.this_node = this_node
    ctx.resource_lock = resource_lock


def test_start_stop():
    global resource_lock, ctx

    worker = nodechecker.worker.Worker(ctx)
    assert worker.isAlive() is False

    worker.start()
    assert worker.isAlive() is True

    worker.shutdown()
    worker.join()
    assert worker.isAlive() is False

def test_send_receive_heartbeats():
    global resource_lock, ctx

    # Setup
    listener_node = nodechecker.node.Node(ip_address='5.5.5.5', port=11111)
    ctx2 = nodechecker.context.Context()
    ctx2.this_node = listener_node
    ctx2.resource_lock = resource_lock
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx2)
    
    worker = nodechecker.worker.Worker(ctx)
    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111)
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911)
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911)
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911)
    ctx.node_list = [n1, n2, n3, ctx.this_node]

    # Run
    udp_listener.start()
    worker._send_heartbeats()

    time.sleep(5)

    worker._cancel_timers()
    



    # Verification

    time.sleep(1)
    print("*****awake, shutting down udp_listener")
    udp_listener.shutdown()
    udp_listener.join()
    assert udp_listener.isAlive() is False








