import os
import inspect
import threading
import nodechecker.config
import nodechecker.node
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

'''
def test_start_stop():
    pass
    #TODO:to be implemented once the structure of raw data is visible
'''










