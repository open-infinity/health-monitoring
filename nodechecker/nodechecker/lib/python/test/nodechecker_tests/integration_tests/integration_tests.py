
import os
import inspect
import nodechecker.notification.notification
import nodechecker.notification.snmp
import nodechecker.config
import nodechecker.node
import nodechecker.nodechecker
import nodechecker.control.servicemanager
from mock import MagicMock
from datetime import datetime

node_manager = None
conf = None


def setup_module():
    global node_manager, conf

    # Create config file reader
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))

    # Create mock node_manager
    node_manager = nodechecker.control.nodemanager.NodeManager(conf)
    node_manager.configure_node_as_master = MagicMock()
    node_manager.configure_node_as_slave = MagicMock()

    # Configure path to healhmonitoring directory structure to be used for testing
    now = datetime.now()
    sub_dir_name = "".join(['hm_root', '-', str(now.year), '-', str(now.month), '-',
                            str(now.day), '-', str(now.hour), '-', str(now.minute),
                            '-', str(now.second)])
    conf.hm_root = os.path.join(test_dir, 'output', sub_dir_name)


def teardown_module():
    pass


def test_start():
    global node_manager, conf
    print('enter test_start()')
    #self.node_manager.configure_node_as_slave(1, 2)
    assert 1 == 1
    #nodechecker.nodechecker.main()
    #service_manager = nodechecker.control.servicemanager.ServiceManager(conf, user=user)
    #service_manager.start_services()
    node_manager.configure_node_as_slave('1.2.3.4',8811,'1.2.3.4',83)
    nodechecker.nodechecker.start(conf, node_manager)


def test_start_2():
    print('enter test_start_2()')
    assert True