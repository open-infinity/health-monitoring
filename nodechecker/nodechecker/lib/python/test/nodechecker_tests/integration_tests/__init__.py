
import os
import sys
import shutil
import inspect
import nodechecker.notification.notification
import nodechecker.notification.snmp
import nodechecker.config
import nodechecker.node
import nodechecker.main
import nodechecker.control.servicemanager
from mock import MagicMock
from datetime import datetime


def setup_package():
    node = nodechecker.node.Node(hostname='test1', port=10, cloud_zone='cloudzone1',
                                      ip_address_public='1.2.3.4', instance_id=1,
                                      cluster_id=1, machine_id=1)

    # Create config file reader
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    conf_file = os.path.join(test_dir, 'nodechecker.conf')
    conf = nodechecker.config.Config(conf_file)

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

    # Create directory structure for testing
    nodechecker_home = os.path.join(conf.hm_root, conf.nodechecker_home)
    collectd_home = os.path.join(conf.hm_root, conf.collectd_home)
    pound_home = os.path.join(conf.hm_root, conf.pound_home)
    rrd_http_server_home = os.path.join(conf.hm_root, conf.rrd_http_server_home)

    create_tree(test_dir, nodechecker_home, collectd_home, pound_home, rrd_http_server_home)


def create_tree(test_dir, nodechecker_home, collectd_home, pound_home, rrd_http_server_home):
    # traverse 5 levels up in directory tree, to nodechecker root dir
    # TODO: is there some search functcion available? implement one if not
    p1_dir = os.path.abspath(os.path.join(test_dir, os.pardir))
    p2_dir = os.path.abspath(os.path.join(p1_dir, os.pardir))
    p3_dir = os.path.abspath(os.path.join(p2_dir, os.pardir))
    p4_dir = os.path.abspath(os.path.join(p3_dir, os.pardir))
    src_dir = os.path.abspath(os.path.join(p4_dir, os.pardir))

    var_dir = os.path.join(src_dir, 'opt', 'monitoring', 'var')
    try:
        shutil.copytree(var_dir, os.path.join(nodechecker_home, 'var'))
        os.makedirs(os.path.join(nodechecker_home, 'var', 'log'))
        os.makedirs(collectd_home)
        os.makedirs(pound_home)

        os.makedirs(rrd_http_server_home)
        etc_dir = os.path.join(test_dir, 'data', 'hm_root', 'nodechecker', 'etc')
        shutil.copytree(etc_dir, os.path.join(nodechecker_home, 'etc'))
    except:
        print(sys.exc_info())
        
        

