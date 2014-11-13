import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
import nodechecker.manager
import nodechecker.context
import nodechecker.udp_listener
import nodechecker.timer
from mock import MagicMock
import time


conf = None
runtime = None
resource_lock = None
ctx = None


def setup():
    global resource_lock, ctx
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()

    ctx = nodechecker.context.Context()
    ctx.this_node = this_node
    ctx.resource_lock = resource_lock


def test_start_stop():
    global resource_lock, ctx

    #Setup
    ctx.active_node_list = [ctx.this_node]
    ctx.node_manager = MagicMock()
    ctx.nodelist_reader = MagicMock()
    ctx.ntf_manager = MagicMock()
    ctx.ntf_reader = MagicMock()
    manager = nodechecker.manager.Manager(ctx)
    print("role:" + ctx.this_node.role)
    manager._logger = MagicMock()
    assert manager.isAlive() is False

    # Run
    manager.start()
    assert manager.isAlive() is True
    time.sleep(5)
    print("*************manager shutdown**************")
    manager.shutdown()
    manager.join()

    # Verification
    assert manager.isAlive() is False

