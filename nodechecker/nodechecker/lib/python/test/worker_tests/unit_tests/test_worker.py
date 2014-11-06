import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.worker
import time
import nodechecker.context

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


def test_start_stop():
    global conf, resource_lock, ctx

    worker = nodechecker.worker.Worker(ctx, resource_lock)
    assert worker.isAlive() is False

    worker.start()
    assert worker.isAlive() is True

    worker.shutdown()
    #time.sleep(5)
    #assert worker.isAlive() is False


def test_udp_listener_start():
    global conf, resource_lock, ctx

    #worker = nodechecker.worker.Worker(ctx, resource_lock)


    pass





