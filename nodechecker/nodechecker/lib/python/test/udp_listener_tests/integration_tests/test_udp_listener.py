import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.manager
import time
import nodechecker.context
import nodechecker.udp_listener
import nodechecker.node

conf = None
runtime = None
resource_lock = None
ctx = None


def setup():
    global conf, resource_lock, ctx
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    p1_dir = os.path.abspath(os.path.join(test_dir, os.pardir))
    p2_dir = os.path.abspath(os.path.join(p1_dir, os.pardir))
    conf = nodechecker.config.Config(os.path.join(p2_dir, 'conf', 'nodechecker', 'etc', 'nodechecker.conf'))
    resource_lock = threading.RLock()
    ctx = nodechecker.context.Context()


def test_handle_heartbeat():
    global conf, resource_lock, ctx
    this_node = nodechecker.node.Node()
    ctx.this_node = this_node

    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx)
    assert udp_listener.isAlive() is False

    udp_listener.start()
    assert udp_listener.isAlive() is True

    time.sleep(1)
    print("awake, shutting down udp_listener")
    udp_listener.shutdown()
    udp_listener.join()
    assert udp_listener.isAlive() is False









