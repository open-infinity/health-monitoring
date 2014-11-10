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
    global conf, resource_lock, ctx
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()

    ctx = nodechecker.context.Context()
    ctx.this_node = this_node
    ctx.resource_lock = resource_lock


def test_start_stop():
    global conf, resource_lock, ctx

    worker = nodechecker.worker.Worker(ctx)
    assert worker.isAlive() is False

    worker.start()
    assert worker.isAlive() is True

    worker.shutdown()
    worker.join()
    assert worker.isAlive() is False

def test_send_receive_heartbeats():
    global conf, resource_lock, ctx

    # Setup
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    worker = nodechecker.worker.Worker(ctx)
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4')
    n1 = nodechecker.node.Node(ip_address='127.0.0.1')
    n2 = nodechecker.node.Node(ip_address='2.2.2.2')
    n3 = nodechecker.node.Node(ip_address='3.3.3.3')
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








