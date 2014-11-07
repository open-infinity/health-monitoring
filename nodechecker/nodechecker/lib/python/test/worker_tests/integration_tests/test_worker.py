import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.worker
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


def test_start_stop():
    global conf, resource_lock, ctx

    worker = nodechecker.worker.Worker(ctx)
    assert worker.isAlive() is False

    worker.start()
    assert worker.isAlive() is True

    worker.shutdown()
    worker.join()
    assert worker.isAlive() is False


